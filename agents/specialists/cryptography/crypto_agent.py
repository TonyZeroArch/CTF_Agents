"""
Cryptography Specialist Agent

Specialized agent for solving cryptography-based CTF challenges.
"""

from typing import Dict, Any, List, Tuple
from agents.base_agent import BaseAgent, AgentType
import re


class CryptographyAgent(BaseAgent):
    """
    Specialist agent for cryptography challenges.
    """

    def __init__(self, agent_id: str = "crypto_agent"):
        super().__init__(agent_id, AgentType.SPECIALIST)
        self.capabilities = [
            "crypto",
            "cryptography",
            "encryption",
            "decryption",
            "hash_cracking",
            "encoding",
            "rsa",
            "aes",
            "classical_ciphers",
        ]

        # Tiny but useful English model for Caesar scoring
        self.common_words = {
            "the", "and", "that", "have", "for", "not", "with", "you", "this",
            "but", "his", "from", "they", "say", "her", "she", "will", "one",
            "all", "would", "there", "their", "what", "about", "which", "when",
            "make", "can", "like", "time", "just", "know", "take", "into",
            "year", "your", "good", "some", "could", "them", "see", "other",
            "than", "then", "now", "look", "only", "come", "its", "over",
            "think", "also", "back", "after", "use", "two", "how", "our",
            "work", "first", "well", "way", "even", "new", "want", "because",
            "any", "these", "give", "day", "most", "us", "he", "it", "in",
            "to", "of", "if", "had", "anything", "confidential", "cipher",
            "wrote", "word", "letters", "alphabet", "order", "made", "out",
            "hello", "world",
        }

    def analyze_challenge(self, challenge: Dict[str, Any]) -> Dict[str, Any]:
        description = challenge.get("description", "").lower()
        hints = " ".join(challenge.get("hints", [])).lower()
        metadata = challenge.get("metadata", {})

        cipher_types = []

        if any(keyword in description for keyword in ["caesar", "shift", "rot"]):
            cipher_types.append("caesar_cipher")
        if any(keyword in hints for keyword in ["shift", "caesar", "rot"]):
            cipher_types.append("caesar_cipher")
        if metadata.get("cipher_type") == "caesar":
            cipher_types.append("caesar_cipher")

        if any(keyword in description for keyword in ["rsa", "public key", "private key"]):
            cipher_types.append("rsa")
        if "base64" in description:
            cipher_types.append("base64")
        if any(keyword in description for keyword in ["hash", "md5", "sha"]):
            cipher_types.append("hash")
        if "aes" in description:
            cipher_types.append("aes")

        cipher_types = sorted(set(cipher_types))
        confidence = 0.9 if challenge.get("category") == "crypto" else 0.1

        return {
            "agent_id": self.agent_id,
            "can_handle": challenge.get("category") == "crypto",
            "confidence": confidence,
            "detected_types": cipher_types,
            "approach": self._plan_approach(cipher_types),
        }

    def solve_challenge(self, challenge: Dict[str, Any]) -> Dict[str, Any]:
        analysis = self.analyze_challenge(challenge)

        steps: List[str] = []
        flag = None

        steps.append("Analyzed cipher/encoding type")
        steps.append("Detected types: " + ", ".join(analysis["detected_types"]))

        if "caesar_cipher" in analysis["detected_types"]:
            steps.append("Attempting Caesar brute force (shifts 1-25)")

            cipher_text = self._extract_ciphertext(challenge)
            best_shift, best_plaintext, best_score = self._best_caesar_candidate(cipher_text)

            steps.append(f"Chosen shift: {best_shift}")
            steps.append(f"Recovered plaintext: {best_plaintext}")
            steps.append(f"English score: {best_score:.2f}")

            flag = best_plaintext
        else:
            steps.append("No implemented solver for detected types yet")

        return {
            "challenge_id": challenge.get("id"),
            "agent_id": self.agent_id,
            "status": "solved" if flag else "attempted",
            "flag": flag,
            "steps": steps,
            "cipher_types": analysis["detected_types"],
        }

    def get_capabilities(self) -> List[str]:
        return self.capabilities

    def _plan_approach(self, cipher_types: List[str]) -> str:
        if not cipher_types:
            return "General cryptanalysis and cipher identification"
        return f"Focus on {', '.join(cipher_types)}"

    def _extract_ciphertext(self, challenge: Dict[str, Any]) -> str:
        """
        Extract ciphertext from description.
        Prefers quoted text, otherwise falls back to the full description.
        """
        description = challenge.get("description", "")

        # Prefer single-quoted or double-quoted payloads
        match = re.search(r"'([^']+)'", description)
        if match:
            return match.group(1).strip()

        match = re.search(r'"([^"]+)"', description)
        if match:
            return match.group(1).strip()

        return description.strip()

    def _best_caesar_candidate(self, cipher_text: str) -> Tuple[int, str, float]:
        candidates: List[Tuple[int, str, float]] = []

        for shift in range(1, 26):
            plain = self._caesar_decrypt(cipher_text, shift)
            score = self._score_english(plain)
            candidates.append((shift, plain, score))

        candidates.sort(key=lambda x: x[2], reverse=True)
        return candidates[0]

    def _score_english(self, text: str) -> float:
        """
        Score plaintext candidates for 'English-likeness'.
        Higher is better.
        """
        lowered = text.lower()
        words = re.findall(r"[a-z]+", lowered)

        if not words:
            return float("-inf")

        score = 0.0

        # Strong signal: exact common words
        common_word_hits = sum(1 for w in words if w in self.common_words)
        score += common_word_hits * 8.0

        # Medium signal: common short words appear anywhere
        for token in [" the ", " and ", " to ", " of ", " in ", " he ", " it ", " if "]:
            if token in f" {lowered} ":
                score += 6.0

        # Reward vowels somewhat, but not too much
        letters = [c for c in lowered if c.isalpha()]
        if letters:
            vowel_ratio = sum(c in "aeiou" for c in letters) / len(letters)
            # English usually lands in a sane middle range
            if 0.25 <= vowel_ratio <= 0.45:
                score += 8.0
            else:
                score -= abs(vowel_ratio - 0.35) * 20.0

        # Reward spaces and readable word lengths
        avg_word_len = sum(len(w) for w in words) / len(words)
        if 2.5 <= avg_word_len <= 7.5:
            score += 4.0

        # Penalize weird punctuation/digit soup
        weird_chars = sum(not (c.isalpha() or c.isspace() or c in ".,!?;:'\"-") for c in text)
        score -= weird_chars * 2.5

        # Penalize unlikely consonant soup chunks
        if re.search(r"[bcdfghjklmnpqrstvwxyz]{6,}", lowered):
            score -= 10.0

        # Reward repeated common endings/patterns
        for pattern in ["ing", "tion", "ed", "er", "th", "he", "an", "re"]:
            score += lowered.count(pattern) * 0.8

        return score

    def _caesar_decrypt(self, text: str, shift: int) -> str:
        result = []

        for ch in text:
            if ch.isalpha():
                base = ord("A") if ch.isupper() else ord("a")
                result.append(chr((ord(ch) - base - shift) % 26 + base))
            else:
                result.append(ch)

        return "".join(result)