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

### 7. Set Up Pre-commit Hook
- Created `.git/hooks/pre-commit` (not tracked by git, lives in `.git/`)
- Made executable with `chmod +x`
- Runs on every commit: `uv run ruff check . && uv run ruff format --check .`
- Blocks commits if lint errors or formatting issues are found
- Verified hook passes on current codebase

### 8. Add mypy (expanded from official docs)
- `uv add --dev mypy`
- Configured `[tool.mypy]` in `pyproject.toml` based on official config docs:
  - `strict = true` — enables all 13 optional checks in one flag
  - `warn_unreachable`, `strict_bytes` — additional strictness
  - AI-optimised output: `show_error_context`, `show_error_codes`, `show_error_code_links`, `show_column_numbers`, `pretty`
  - `[[tool.mypy.overrides]]` relaxes strictness for `tests.*`
- `main.py` rewritten to exercise 10 rule categories (generics, Optional, decorators, Protocol, strict_bytes, etc.)
- Gotcha: `** 0.5` returns `Any` under strict — use `math.sqrt()` instead
- Gotcha: Python 3.12 type param syntax (`def f[F: Callable]`) required by `UP047`
- Run with: `uv run mypy .`

### 9. Add Pyright (second type checking layer)
- `uv add --dev pyright`
- Configured `[tool.pyright]` in `pyproject.toml` based on official docs:
  - `typeCheckingMode = "strict"` — enables full strict rule set
  - `strictListInference`, `strictDictionaryInference`, `strictSetInference` — no implicit `Any` in collection literals
  - `disableBytesTypePromotions = true` — mirrors mypy's `strict_bytes`
  - Opt-in extras (not on even in strict): `reportUnreachable`, `reportImportCycles`, `reportUninitializedInstanceVariable`, `reportUnnecessaryTypeIgnoreComment`
- Both mypy and pyright pass clean on `main.py` (0 errors each)
- Run with: `uv run pyright`
- Pyright advantage over mypy: better narrowing, strict collection inference, `reportMatchNotExhaustive`, `reportImportCycles`

### 10. Add pytest, pytest-asyncio, pytest-cov
- `uv add --dev pytest pytest-asyncio pytest-cov`
- Configured `[tool.pytest.ini_options]` in `pyproject.toml`:
  - `asyncio_mode = "auto"` — no `@pytest.mark.asyncio` decorator needed
  - `asyncio_default_fixture_loop_scope = "function"` — explicit to avoid deprecation warnings
  - `addopts = "--tb=short -v --cov --cov-report=term-missing"` — coverage on every run
- Added `[tool.coverage.run]` and `[tool.coverage.report]` sections
- Added `async_add()` to `main.py` to demonstrate pytest-asyncio pattern
- Created `tests/__init__.py` and `tests/test_main.py` with 24 tests:
  - 20 sync unit tests covering all public functions
  - 3 async tests (`test_async_add*`) using auto mode (no decorator)
  - 1 async fixture test (`test_async_fixture`)
- Updated `.gitignore` with `.pytest_cache`, `.mypy_cache`, `htmlcov`, `.coverage`
- Gotcha: `pytest.approx` has partially-unknown stubs under pyright strict — use `math.isclose` instead
- Run with: `uv run pytest`

### 11. Add Structured Logging with structlog
- `uv add structlog` (structlog 25.5.0, production dependency)
- Created `app/` package layout: `app/__init__.py`, `app/core/__init__.py`, `app/core/tests/__init__.py`
- Created `app/core/logging.py` with:
  - `request_id_var: ContextVar[str]` — module-level context variable for request correlation
  - `set_request_id(request_id=None) -> str` — stores UUID4 (or supplied value) in ContextVar
  - `get_request_id() -> str` — reads from ContextVar
  - `setup_logging(log_level="INFO") -> None` — configures structlog globally with processor chain:
    - `_add_request_id` — injects request_id into every event dict
    - `structlog.stdlib.add_log_level` — adds `level` field
    - `structlog.processors.TimeStamper(fmt="iso")` — ISO-8601 timestamp
    - `structlog.processors.StackInfoRenderer()` — stack_info support
    - `structlog.processors.ExceptionRenderer()` — exc_info → `"exception"` key in JSON
    - `structlog.processors.JSONRenderer()` — final JSON output
  - `get_logger(name=None) -> structlog.stdlib.BoundLogger` — typed logger factory
  - Event naming convention (hybrid dotted namespace): `{domain}.{component}.{action}_{state}`
    - Examples: `user.registration_started`, `database.connection_initialized`, `task.processing_failed`
    - States: `_started`, `_completed`, `_failed`, `_validated`, `_rejected`
- Created `app/main.py` — usage demo with `simulate_registration`, `simulate_db_init`, `simulate_failure`
- Created `app/core/tests/test_logging.py` — 9 tests (TDD: tests written first)
- Updated `pyproject.toml`:
  - ruff per-file-ignores: added `"app/**/tests/**/*.py" = ["S101", "ANN"]`
  - mypy overrides: added `[[tool.mypy.overrides]]` for `app.core.tests.*`
  - pytest testpaths: `["tests", "app"]`
- Gotchas:
  - `add_logger_name` processor requires a stdlib logger — incompatible with `PrintLoggerFactory` (no `.name` attr); remove it
  - `PrintLoggerFactory(file=sys.stdout)` required for pytest `capsys` capture
  - `cache_logger_on_first_use=False` required when `setup_logging()` is called multiple times in tests
  - `cast(BoundLogger, ...)` was redundant — mypy infers `proxy.bind()` already returns `BoundLogger`
  - ContextVar state bleeds between tests — add autouse fixture: `token = request_id_var.set(""); yield; request_id_var.reset(token)`
- Run demo: `uv run python -m app.main`
- 33 total tests passing (24 root + 9 logging); ruff, mypy, pyright all clean

### 12. Move External Docs into `.claude/`
- Moved `external_docs/` → `.claude/external_docs/` to co-locate reference docs with Claude config
- Files moved:
  - `.claude/external_docs/ai-coding-project-setup-guide.md`
  - `.claude/external_docs/vertical-slice-architecture-setup-guide.md`
- Updated MEMORY.md to reflect new paths

### 13. Add Docker Setup with uv Multi-Stage Build
- Reference: `https://docs.astral.sh/uv/guides/integration/docker/`
- Created `Dockerfile` (multi-stage):
  - Builder: `python:3.12-slim-bookworm` + uv binary copied from `ghcr.io/astral-sh/uv:latest` distroless image
  - `UV_COMPILE_BYTECODE=1` — bytecode compilation for faster startup
  - `UV_LINK_MODE=copy` — required for cache mounts across separate filesystems
  - Deps installed in a separate cached layer (`--no-install-project --no-dev`) before copying source
  - Runtime: clean `python:3.12-slim-bookworm` with only `.venv` + `app/` copied from builder
  - No uv, no build tools in the final image
- Created `.dockerignore`:
  - Excludes `.venv`, bytecode, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `.pyright`
  - Excludes `.git`, `.env`, `.firecrawl`, `.claude`, `docs/`, `dist/`
- Created `docker-compose.yml`:
  - Port `8123:8123`, `.env` support (optional), `PYTHONUNBUFFERED=1`
  - Bind mount `.:/app` for live code changes; anonymous `/app/.venv` to preserve container's packages
- Build: `docker build -t aa-live-aitemplate-build .`
- Image size: 213MB (base slim + structlog only)
- Container runs and produces structured JSON logs as expected
- Gotcha: `--no-editable` requires a `[build-system]` in pyproject.toml to build a wheel; omitted since project has none — re-enable when FastAPI/hatchling is added

## TODO
## Personal TODO
- something to include later, first do PRD, then finalize the architecture and tech stack and then setup the project template
- When finalize the template - ask AI, what tools I can / should use, the external documentation for it and then create the "prompt" to setup the tool/framework, 
