# Project Setup Summary

<!--
INSTRUCTIONS FOR CLAUDE (read at the start of every session):
- This file is the running log of everything built in this project.
- At the end of each session, or when the user asks, append a new numbered section
  under "Steps Completed" describing what was done, commands run, and any gotchas.
- When a TODO item is completed, move it from the TODO section into Steps Completed.
- Keep entries concise: what was done, why, and the exact commands used.
- Ask the user "Should I update summary.md?" before closing out any session.
-->

##For reference
https://github.com/dynamous-community/agentic-coding-course/blob/main/module_5/workshop_ai_optimized_codebase/external-docs/ai-coding-project-setup-guide.md

## Steps Completed

### 1. Initialize Project
- `uv init`
- Python 3.12, managed with `uv`
#To check if template was created
- uv run main.py 

### 2. Add `.gitignore`
- Covers: `.venv`, `__pycache__`, `*.pyc`, `.env`, `dist`, `*.egg-info`, `.ruff_cache`, `.firecrawl`

### 3. Create `CLAUDE.md`
- Project overview and common commands for Claude Code

### 4. Set Up Ruff
- `uv add --dev ruff`
- Configured in `pyproject.toml` with AI-optimized rule set:
  - `E, W` — pycodestyle errors/warnings
  - `F` — Pyflakes
  - `I` — isort
  - `B` — flake8-bugbear
  - `S` — flake8-bandit (security)
  - `ANN` — flake8-annotations (type hints)
  - `UP` — pyupgrade
  - `N` — pep8-naming
  - `A` — flake8-builtins
  - `C4` — flake8-comprehensions
  - `SIM` — flake8-simplify
  - `RUF` — Ruff-specific rules
- `fixable = ["ALL"]`
- `ignore = ["S311"]`
- `per-file-ignores`: `tests/**/*.py` → `["S101", "ANN"]`, `__init__.py` → `["F401"]`
- Note: `ANN101`/`ANN102` removed from Ruff — do not add to ignore

### 5. Write `main.py`
- Simple script with type annotations to validate Ruff setup

### 6. Test Ruff
- `uv run ruff check --output-format full main.py` — full output for AI self-correction context
- `uv run ruff check --fix main.py` — apply auto-fixes
- `uv run ruff format main.py` — format
- `uv run ruff format --check main.py` — check formatting without modifying
- Caught and fixed 3 issues: `I001` (import order), `UP015` (unnecessary open mode), `E711` (None comparison)

## TODO
- Set up pre-commit hook: `uv run ruff check . && uv run ruff format --check .`
- Review `external_docs/ai-coding-project-setup-guide.md` — check if anything else needs to be added to Ruff config
