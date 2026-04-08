from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from openai import OpenAI


@dataclass
class ChallengeAnalysis:
    category_guess: str
    confidence: float
    reasoning: str
    recommended_target: str
    recommended_action: str
    detected_indicators: List[str]


class LLMReasoner:
    """
    Uses OpenAI Responses API if OPENAI_API_KEY is present.
    Falls back to heuristics if not.
    """

    def __init__(self, client: Optional[Any] = None, model: str = "gpt-5.4"):
        if client is not None:
            self.client = client
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            self.client = OpenAI(api_key=api_key) if api_key else None

        self.model = model

    def analyze_challenge(self, challenge: Dict[str, Any]) -> ChallengeAnalysis:
        if self.client is None:
            return self._heuristic_analysis(challenge)

        prompt = self._build_analysis_prompt(challenge)
        raw = self._call_llm(prompt)

        try:
            data = json.loads(raw)
            return ChallengeAnalysis(
                category_guess=data.get("category_guess", "unknown"),
                confidence=float(data.get("confidence", 0.0)),
                reasoning=data.get("reasoning", "No reasoning provided."),
                recommended_target=data.get("recommended_target", "none"),
                recommended_action=data.get("recommended_action", "stop"),
                detected_indicators=data.get("detected_indicators", []),
            )
        except Exception:
            return self._heuristic_analysis(challenge)

    def choose_next_action(
        self,
        challenge: Dict[str, Any],
        analysis: ChallengeAnalysis,
        history: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if self.client is None:
            return self._heuristic_next_action(challenge, analysis, history)

        prompt = self._build_next_action_prompt(challenge, analysis, history)
        raw = self._call_llm(prompt)

        try:
            return json.loads(raw)
        except Exception:
            return self._heuristic_next_action(challenge, analysis, history)

    def _call_llm(self, prompt: str) -> str:
        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
            )
            return response.output_text
        except Exception as e:
            print(f"[LLM ERROR] Falling back to heuristics: {e}")
            return ""

    def _build_analysis_prompt(self, challenge: Dict[str, Any]) -> str:
        return f"""
You are analyzing a CTF challenge for routing and planning.

Return ONLY valid JSON with this shape:
{{
  "category_guess": "crypto|web|reverse|pwn|forensics|osint|misc|unknown",
  "confidence": 0.0,
  "reasoning": "short explanation",
  "recommended_target": "crypto_agent|browser_snapshot|tony_htb_sql|none",
  "recommended_action": "run_agent|run_tool|stop",
  "detected_indicators": ["indicator1", "indicator2"]
}}

Challenge:
{json.dumps(challenge, indent=2)}
""".strip()

    def _build_next_action_prompt(
        self,
        challenge: Dict[str, Any],
        analysis: ChallengeAnalysis,
        history: List[Dict[str, Any]],
    ) -> str:
        return f"""
You are deciding the next step in a CTF agent workflow.

Return ONLY valid JSON with this shape:
{{
  "next_action": "run_agent|run_tool|stop",
  "target": "crypto_agent|browser_snapshot|tony_htb_sql|none",
  "reasoning": "short explanation",
  "inputs": {{}}
}}

Challenge:
{json.dumps(challenge, indent=2)}

Analysis:
{json.dumps(asdict(analysis), indent=2)}

History:
{json.dumps(history, indent=2)}
""".strip()

    def _looks_like_base64(self, text: str) -> bool:
        compact = re.sub(r"\s+", "", text)
        if len(compact) < 8 or len(compact) % 4 != 0:
            return False
        return bool(re.fullmatch(r"[A-Za-z0-9+/=]+", compact))

    def _looks_like_hex(self, text: str) -> bool:
        compact = re.sub(r"\s+", "", text)
        return (
            len(compact) >= 8
            and len(compact) % 2 == 0
            and bool(re.fullmatch(r"[0-9a-fA-F]+", compact))
        )

    def _looks_like_textual_cipher(self, text: str) -> bool:
        words = re.findall(r"[A-Za-z]+", text)
        return len(words) >= 3 and sum(len(w) for w in words) >= 12

    def _heuristic_analysis(self, challenge: Dict[str, Any]) -> ChallengeAnalysis:
        raw_text = " ".join([
            challenge.get("name", ""),
            challenge.get("description", ""),
            " ".join(challenge.get("hints", [])),
            " ".join(challenge.get("tags", [])),
            json.dumps(challenge.get("metadata", {})),
        ])

        text = raw_text.lower()
        indicators: List[str] = []

        has_crypto_keywords = any(
            word in text
            for word in ["cipher", "decrypt", "base64", "hex", "xor", "caesar", "rot", "encode", "decode"]
        )
        looks_base64 = self._looks_like_base64(raw_text)
        looks_hex = self._looks_like_hex(raw_text)
        looks_textual_cipher = self._looks_like_textual_cipher(raw_text)

        if has_crypto_keywords or looks_base64 or looks_hex:
            if has_crypto_keywords:
                indicators.append("crypto_terms")
            if looks_base64:
                indicators.append("base64_pattern")
            if looks_hex:
                indicators.append("hex_pattern")
            if looks_textual_cipher:
                indicators.append("textual_cipher_pattern")

            return ChallengeAnalysis(
                category_guess="crypto",
                confidence=0.93,
                reasoning="Detected crypto-related terms or encoded/cipher-like patterns.",
                recommended_target="crypto_agent",
                recommended_action="run_agent",
                detected_indicators=indicators,
            )

        if any(word in text for word in ["sqli", "sql injection", "login bypass", "union select"]):
            indicators.append("sqli_terms")
            return ChallengeAnalysis(
                category_guess="web",
                confidence=0.91,
                reasoning="Detected SQL injection indicators.",
                recommended_target="tony_htb_sql",
                recommended_action="run_tool",
                detected_indicators=indicators,
            )

        if any(word in text for word in ["url", "http", "login", "form", "page", "cookie", "endpoint"]):
            indicators.append("web_terms")
            return ChallengeAnalysis(
                category_guess="web",
                confidence=0.88,
                reasoning="Detected web-related terms.",
                recommended_target="browser_snapshot",
                recommended_action="run_tool",
                detected_indicators=indicators,
            )

        return ChallengeAnalysis(
            category_guess=challenge.get("category", "unknown"),
            confidence=0.50,
            reasoning="No strong indicators found.",
            recommended_target="none",
            recommended_action="stop",
            detected_indicators=indicators,
        )

    def _heuristic_next_action(
        self,
        challenge: Dict[str, Any],
        analysis: ChallengeAnalysis,
        history: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if analysis.recommended_target == "crypto_agent":
            return {
                "next_action": "run_agent",
                "target": "crypto_agent",
                "reasoning": "Crypto challenge detected.",
                "inputs": {},
            }

        if analysis.recommended_target == "browser_snapshot":
            return {
                "next_action": "run_tool",
                "target": "browser_snapshot",
                "reasoning": "Web challenge detected.",
                "inputs": {
                    "url": challenge.get("url") or challenge.get("target", {}).get("url", "")
                },
            }

        if analysis.recommended_target == "tony_htb_sql":
            return {
                "next_action": "run_tool",
                "target": "tony_htb_sql",
                "reasoning": "SQL injection likely.",
                "inputs": {
                    "url": challenge.get("url") or challenge.get("target", {}).get("url", "")
                },
            }

        return {
            "next_action": "stop",
            "target": "none",
            "reasoning": "No confident next step.",
            "inputs": {},
        }