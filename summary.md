# Project Setup Summary

<!--
INSTRUCTIONS FOR CLAUDE (read at the start of every session):
- This file is the running log of everything built in this project.
- At the end of each session, or when the user asks, append a new numbered section
  under "Steps Completed" describing what was done, commands run, and any gotchas.
- When a TODO item is completed, move it from the TODO section into Steps Completed.
- Keep entries concise: what was done, why, and the exact commands used.
- Ask the user "Should I update summary.md?" before closing out any session.

https://github.com/dynamous-community/agentic-coding-course/tree/main/module_5/workshop_ai_optimized_codebase/live_template_build
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

### 14. Add FastAPI with Pydantic Settings and Request Logging Middleware
- Reference: `.claude/external_docs/vertical-slice-architecture-setup-guide.md` + `https://fastapi.tiangolo.com/advanced/events/`
- Installed: `fastapi`, `uvicorn[standard]`, `pydantic-settings`, `python-dotenv` (prod); `httpx` (dev)
- Created `app/core/config.py`:
  - `Settings(BaseSettings)` with fields: `app_name`, `version`, `environment`, `log_level`, `api_prefix`, `allowed_origins`
  - `_CommaFallbackEnvSource(EnvSettingsSource)` — overrides `decode_complex_value` to fall back to comma-split for list fields (pydantic-settings v2 requires JSON for list types by default; this enables `ALLOWED_ORIGINS=a.com,b.com`)
  - `settings_customise_sources` classmethod swaps in the custom source
  - `@lru_cache get_settings()` — cached singleton
- Created `app/core/middleware.py`:
  - `RequestLoggingMiddleware(BaseHTTPMiddleware)` — sets request_id from `X-Request-ID` header or generates UUID4, logs `request.started` / `request.completed` / `request.failed`, adds `X-Request-ID` to response headers
  - `setup_middleware(app)` — adds `RequestLoggingMiddleware` + `CORSMiddleware` with `settings.allowed_origins`
- Rewrote `app/main.py` as FastAPI application:
  - `@asynccontextmanager lifespan(app)` — calls `setup_logging()`, logs `application.startup` / `application.shutdown`
  - `FastAPI(title=..., version=..., lifespan=lifespan)` with `setup_middleware(app)` at module level
  - `GET /` root endpoint returns `message`, `version`, `docs`
  - `if __name__ == "__main__":` runs uvicorn on port 8123
- Created `.env.example` with commented application settings
- Updated `pyproject.toml`:
  - `name = "vsa-fastapi-project"`, updated description
  - `[tool.ruff.lint.isort] known-first-party = ["app"]`
  - New `[[tool.mypy.overrides]]` for `app.tests.*`
  - `reportUnusedFunction = "none"` — suppresses pyright false positives for FastAPI route handlers in test fixtures
- Created test files:
  - `app/core/tests/test_config.py` — 6 tests (defaults, env vars, caching, CORS parsing)
  - `app/core/tests/test_middleware.py` — 5 tests (request-ID generation, header passthrough, log event mocking, CORS OPTIONS)
  - `app/tests/test_main.py` — 4 tests (root endpoint structure, /docs, /openapi.json, CORS headers)
  - `app/tests/__init__.py` — new package
- Gotchas:
  - `@field_validator` with `mode="before"` does NOT intercept pydantic-settings env parsing (source parses first) — must override `decode_complex_value` in `EnvSettingsSource` subclass
  - Module-level logger (`get_logger().bind()`) binds to the logger factory at import time — calling `setup_logging()` in a test does not update it; use `patch("app.core.middleware.logger")` to mock
  - `capsys` captures structlog output only if `setup_logging()` was called after capsys fixture replaced `sys.stdout` — but module-level loggers bypass this; mock instead
  - `reportUnusedFunction` pyright strict false positive for `@app.get()`-decorated inner functions in test fixtures
- Run: `uv run uvicorn app.main:app --reload --port 8123`
- 48 total tests passing (24 root + 9 logging + 6 config + 5 middleware + 4 main); ruff, mypy, pyright all clean
- Coverage: 92% overall

### 15. Extract Setup Prompts to setup-prompts.md
- Read `.claude/external_docs/ai-coding-project-setup-guide.md` and extracted all 11 prompts
- Created `setup-prompts.md` in project root with each prompt under a numbered heading, in run order:
  1. Ruff Setup
  2. MyPy Setup
  3. Pyright Setup
  4. Pytest Setup
  5. Structured Logging Setup
  6. Docker Setup
  7. FastAPI + Configuration + Middleware
  8. Check Ignore Comments
  9. Validate (full project health check)
  10. Database Infrastructure (PostgreSQL + Health Checks + Alembic)
  11. Shared Utilities & Patterns
- File paths in prompts updated to use `.claude/external-docs/` (user-adjusted from `.agents/external-docs/`)

### 17. Full Project Validation
- Ran comprehensive validation: tests, type checking, linting, local server, Docker
- **Tests:** 48/48 passed, 92% coverage
- **mypy:** clean (12 source files)
- **pyright:** 0 errors, 0 warnings, 0 informations
- **ruff:** all checks passed
- **Local server:** `GET /`, `GET /docs` both 200; `x-request-id` header present
- **Docker:** build successful, container healthy, endpoints 200, structured JSON logs confirmed
- **Bug fixed:** `app/main.py:51` — `host="127.0.0.1"` → `host="0.0.0.0"` (container was unreachable from host)

### 16. Audit Ignore Comments
- Scanned all `*.py` files for `# noqa` and `# type: ignore` suppressions
- Found 2 comments, both in `app/core/config.py:37-38` (`# noqa: ANN401`)
- Both suppress `ANN401` on `decode_complex_value` — an override of `pydantic-settings`' `EnvSettingsSource`, which itself uses `Any` in its signature; no valid alternative exists
- Created `.claude/reports/ignore-comments-report-2026-02-27.md` with analysis and recommendation
- **Verdict:** Keep both — suppressions are correctly scoped and justified by library override contract

## TODO
## Personal TODO
- something to include later, first do PRD, then finalize the architecture and tech stack and then setup the project template
- When finalize the template - ask AI, what tools I can / should use, the external documentation for it and then create the "prompt" to setup the tool/framework, 
- Review all the prompts and see any improvemnet are needed on the specific prompts.
- Also review the /create-prompt command and see if that needs to be reviewed
- Also checkout the create-skill skill to create these commands/skills
