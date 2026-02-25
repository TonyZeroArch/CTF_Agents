
---
# 🟢 Team Best Practices Guide: Using uv for the Full Python Lifecycle
**Goal:** Standardized workflow for **environment parity**, clean **dev/test/prod** tiers, and smooth collaboration using **GitHub + VS Code + uv**.
---
## Phase 1 — Setup & Onboarding
### 1.1 Purpose/Functionality
Ensure every team member:
- Installs uv securely
- Uses consistent Python versions
- Can reproduce the exact same environment
- Avoids system-level Python pollution
---
### 1.2 Install uv (All OS)
#### Linux / macOS (zsh or bash)
**Purpose/Functionality**
Installs uv and ensures your shell can find it (PATH). This is the standard install path for team consistency.
**Command**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# zsh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
# bash (if you use bash instead of zsh)
# echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
# source ~/.bashrc
uv --version
```
> ⚠️ Note (from earlier confusion): If you were in `/bin/sh` (dash), `source` fails. In zsh/bash it works. Prefer **zsh** on Kali as you noted.
#### Windows (PowerShell)
**Purpose/Functionality**
Installs uv on Windows and makes it available in your terminal.
**Command**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
uv --version
```
---
### 1.3 Update uv
**Purpose/Functionality**
Keeps everyone on a current uv version to avoid behavior/flag differences.
**Command**
```bash
uv self update
```
> 🔐 **Golden Rule #1**
> Every developer must use uv for project dependency changes. **No raw `pip install`** for project dependencies
---
## Phase 2 — GitHub + VS Code Repo Creation From Scratch
### 2.1 Purpose/Functionality
Create a repo in GitHub, bring it local via VS Code, and initialize a Python project **exactly once** with uv.
---
### 2.2 Create repo on GitHub
**Purpose/Functionality**
Establishes the shared remote “source of truth”.
**Command**
- Create new repo in GitHub UI (empty repo is fine).
---
### 2.3 Clone repo via VS Code (or terminal)
**Purpose/Functionality**
`git clone` creates the local working copy *and* initializes Git metadata automatically (equivalent effect to `git init` + remote setup + fetch + checkout). This resolves your earlier confusion: **you do not run `git init` after cloning**.
**Command**
```bash
git clone <REPO_URL>
cd <REPO_FOLDER>
code .
```
> 🔐 **Golden Rule #2**
> If you used VS Code “Clone Repository”, Git is already initialized. **Never run `git init` after `git clone`.**
---
## Phase 3 — Project Initialization (uv init is a one-time action)
### 3.1 Purpose/Functionality
Initialize Python project metadata and scaffolding (`pyproject.toml`, `.gitignore`, etc.). This step is done **only once** for the repository.
### 3.2 Command
```bash
uv init
```

> 🔐 **Golden Rule #3**
> `uv init` is done **once per repository**. After that, teammates do **`uv sync`**, not `uv init`.
---
### 3.3 Pin Python version (parity)
**Purpose/Functionality**
Ensures everyone uses the same Python interpreter version (prevents “works on my machine”).
**Command**
```bash
uv python install 3.11
uv python pin 3.11
```
---

### 3.4 Create the virtual environment + lock
**Purpose/Functionality**
Creates `.venv/` and produces/uses `uv.lock`. This is the authoritative, reproducible environment state.
**Command**
```bash
uv sync
```
---
### 3.5 First commit to GitHub
**Purpose/Functionality**
Publishes the baseline so teammates can reproduce the same environment.
**Command**
```bash
git add -A
git commit -m "Initialize project with uv"
git push -u origin main
```
---
## Phase 4 — Environment Strategy (Dev / Test / Prod)
### 4.1 Purpose/Functionality
Separate dependencies by intent to keep environments clean and efficient.
**Venn-set model**
- **Prod (P)**: required to run the application
- **Test (T)**: required only to run tests (CI)
- **Dev (D)**: developer-only tools (linters/formatters/type-checkers)
**Classification Rules**
1) Imported by production code → **Prod**
2) Imported only by tests → **Test**
3) Used only by humans/tools → **Dev**
---
## Phase 5 — Adding / Updating Dependencies (and maintaining uv.lock)
### 5.1 Add runtime (Prod) dependencies
**Purpose/Functionality**
Adds packages required to run the app and updates lock.
**Command**
```bash
uv add fastapi sqlalchemy
uv sync
```
---
### 5.2 Add development-only dependencies (`--dev`)
**Purpose/Functionality**
Adds tooling (ruff/mypy/etc.) to **Dev** set; can be excluded from production with `--no-dev`.
**Command**
```bash
uv add --dev ruff mypy ipython
uv sync
```
---
### 5.3 Add test-only dependencies (`--group test`)
**Purpose/Functionality**
Adds packages needed for testing pipelines without polluting production.
**Command**
```bash
uv add --group test pytest pytest-cov
uv sync
```
---
### 5.4 Update dependencies (team-controlled)
**Purpose/Functionality**
Upgrades a dependency intentionally and keeps everyone aligned via updated lock.
**Command**
```bash
uv add <pkg>@latest
uv sync
```
> 🔐 **Golden Rule #4**
> If `pyproject.toml` changes, **`uv.lock` must change** in the same PR/commit
---
## Phase 6 — Install by Tier (Development / Testing / Production)
### 6.1 Development machine (local dev in VS Code)
**Purpose/Functionality**
Install everything needed locally (runtime + dev + test).
**Command**
```bash
uv sync --group test
```
---
### 6.2 Testing (CI/CD)
**Purpose/Functionality**
Lean test environment: runtime + test only (no dev tools).
**Command**
```bash
uv sync --no-dev --group test
uv run pytest
```
---
### 6.3 Production
**Purpose/Functionality**
Optimized environment: runtime only.
**Command**
```bash
uv sync --no-dev
```
---
### 6.4 Flag comparison table
| Flag | Purpose | Typical use |
|---|---|---|
| `uv add --dev <pkg>` | classify as Dev-only | ruff, mypy, ipython |
| `uv add --group test <pkg>` | classify as Test group | pytest, pytest-cov |
| `uv sync` | reconcile `.venv` with `uv.lock` | daily, onboarding |
| `uv sync --group test` | include test group | dev machines |
| `uv sync --no-dev --group test` | exclude dev, include test | CI |
| `uv sync --no-dev` | runtime only | prod |
| `uv run <cmd>` | run without activation | consistent scripts |
> 🔐 **Golden Rule #5**
> Production must never include dev dependencies.
---
## Phase 7 — Daily Lifecycle Operations
### 7.1 Start of day (stay aligned)
**Purpose/Functionality**
Prevents “works on my machine” drift.
**Command**
```bash
git pull
uv sync
```
### 7.2 Add a dependency (standard sequence)
**Purpose/Functionality**
Records intent + lock + environment in one flow.
**Command**
```bash
uv add <pkg>            # or --dev / --group test
uv sync
git add pyproject.toml uv.lock
git commit -m "Add <pkg>
```
### 7.3 View installed packages (answering your earlier question)
**Purpose/Functionality**
Inspect the actual environment and the dependency graph.
**Command**
```bash
uv pip list
uv tree
uv pip
```
### 7.4 Rebuild environment (clean reset)
**Purpose/Functionality**
`.venv` is disposable; rebuild from lock.
**Command**
```bash
rm -rf .venv
uv
```
> 🔐 **Golden Rule #6**
> `.venv` is disposable. **The lockfile is truth.**
---
## Phase 8 — Team Synchronization (Onboarding after cloning)
### 8.1 Purpose/Functionality
After a teammate clones, they recreate the same environment automatically.
### 8.2 Command
```bash
uv python install
uv sync
```

> 🔐 **Golden Rule #7**
> Teammates run **`uv sync`**, not `uv init`.
---
## Phase 9 — Conflict Resolution (Branch merges with different packages)
### 9.1 Purpose/Functionality
Two branches may add different dependencies. We merge **declarations**, then regenerate a single consistent lock.
### 9.2 Correct procedure
1) Merge PRs normally
2) Resolve `pyproject.toml` to represent intended combined dependencies
3) If `uv.lock` conflicts, **regenerate** it
**Command**
```bash
rm -f uv.lock
uv sync
git add uv.lock
git commit -m "Re-lock dependencies after merge"
```
> 🔐 **Golden Rule #8**
> Never merge `.venv`. Only merge `pyproject.toml` + regenerate `uv.lock` if needed.
---
## Phase 10 — Addressing the Earlier Confusions(FAQ)
### 10.1 “Does git clone include git init?”
**Purpose/Functionality**
Yes in effect: cloning produces a ready-to-use local repo with `.git/`, remote `origin`, and checked-out branch. So you don’t run `git init` afterward.
### 10.2 “Do I always run uv init after cloning?”
**Purpose/Functionality**
Only if the repo is empty and doesn’t have `pyproject.toml`. Otherwise use `uv sync`.
### 10.3 “Do we still need requirements.txt?”
**Purpose/Functionality**
No—`uv.lock` is the authoritative reproducibility artifact. Export only for legacy needs.
**Command**
```bash
uv pip freeze > requirements.txt
```
### 10.4 “Is uv basically venv + pip?”
**Purpose/Functionality**
Workflow can look similar, but uv adds:
- deterministic lock (`uv.lock`)
- consistent environment reconciliation (`uv sync`)
- clean groups (dev/test)
- `uv run` to avoid activation drift
### 10.5 “Does uv still use pip?”
**Purpose/Functionality** 
uv has its own resolver/installer; `uv pip ...` is a compatibility interface (useful for inspection/
---
# Final Policy Summary (Team Standard)
> 🔐 **Golden Rule Set (print this in README / CONTRIBUTING)**
> 1) Always pin Python.
> 2) Always use `uv add` (never raw pip for project deps).
> 3) Always commit `pyproject.toml` + `uv.lock`.
> 4) Never commit `.venv`.
> 5) Dev: `uv sync --group test`
> 6) CI: `uv sync --no-dev --group test`
> 7) Prod: `uv sync --no-dev`
> 8) If lock conflicts on merge: delete and regenerate `uv.lock`.
---
# Final Mental Model
Old way:
```
venv + pip + requirements.txt
```
Modern way:
```
uv = environment manager + resolver + lock manager + runner
```
The lockfile is your reproducibility contract.
---