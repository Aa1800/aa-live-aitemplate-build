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
- Added `# noqa: S104` on that line — ruff flags `0.0.0.0` as S104 (binding to all interfaces); intentional for Docker `__main__` entrypoint

### 16. Audit Ignore Comments
- Scanned all `*.py` files for `# noqa` and `# type: ignore` suppressions
- Found 2 comments, both in `app/core/config.py:37-38` (`# noqa: ANN401`)
- Both suppress `ANN401` on `decode_complex_value` — an override of `pydantic-settings`' `EnvSettingsSource`, which itself uses `Any` in its signature; no valid alternative exists
- Created `.claude/reports/ignore-comments-report-2026-02-27.md` with analysis and recommendation
- **Verdict:** Keep both — suppressions are correctly scoped and justified by library override contract

### 18. PostgreSQL Database Infrastructure
- Reference: `.claude/external_docs/vertical-slice-architecture-setup-guide.md`
- Installed: `sqlalchemy[asyncio]`, `asyncpg`, `alembic` (prod)
- **Design doc:** `docs/plans/2026-02-27-database-infrastructure-design.md`
- **Implementation plan:** `docs/plans/2026-02-27-database-infrastructure.md`
- **Execution:** subagent-driven development (11 tasks, fresh subagent per task, two-stage review each)

**New files:**
- `app/core/database.py` — async engine (`pool_pre_ping=True`, `pool_size=5`, `max_overflow=10`, `echo` by env), `AsyncSessionLocal`, `Base(DeclarativeBase)`, `get_db()` dependency
- `app/core/exceptions.py` — `DatabaseError`/`NotFoundError`/`ValidationError` hierarchy; `database_exception_handler` with `_STATUS_MAP` dispatch (`NotFoundError→404`, `ValidationError→422`, `DatabaseError→500`); `setup_exception_handlers(app)`
- `app/core/health.py` — `APIRouter` (no prefix) with `GET /health`, `GET /health/db`, `GET /health/ready`; `# noqa: B008` on `Depends()` lines; `raise HTTPException(...) from exc` (preserves exception chain)
- `alembic/env.py` — async-native: `create_async_engine`, `run_sync(do_run_migrations)`, URL from `settings.database_url`
- `app/tests/conftest.py` — `test_db_engine` + `test_db_session` fixtures for integration tests
- `app/core/tests/test_database.py` — 5 unit tests (engine, Base, get_db generator)
- `app/core/tests/test_exceptions.py` — 6 unit tests (hierarchy, handler JSON, status codes, exc_info)
- `app/core/tests/test_health.py` — 5 unit tests (full app + `dependency_overrides` fixture)
- `app/tests/test_database_integration.py` — 3 integration tests (`@pytest.mark.integration`)

**Updated files:**
- `app/core/config.py` — `database_url: str` (required, no default)
- `app/core/tests/test_config.py` — all `Settings()` calls isolated with `_env_file=None` + monkeypatch (CI-safe)
- `app/main.py` — imports engine/health_router/setup_exception_handlers; lifespan logs `database.connection.initialized/closed`; calls `await engine.dispose()` on shutdown
- `docker-compose.yml` — `db` service: `postgres:18-alpine`, port `5433:5432`, `pg_isready` health check, `postgres_data` named volume; `app` service: `depends_on: db: condition: service_healthy`, `DATABASE_URL` override for Docker networking
- `pyproject.toml` — `integration` pytest marker; alembic excluded from mypy/pyright; ruff per-file-ignores for `alembic/**/*.py`
- `.env.example` — database section with Docker, local, Supabase, Neon, Railway examples (all using `ssl=require`, not `sslmode`)
- `.env` — created (gitignored): `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/obsidian_db`

**Gotchas caught during implementation:**
- `patch.object(instance, "__call__", ...)` doesn't work for dunder methods — patch the module-level name instead: `patch.object(db_module, "AsyncSessionLocal", ...)`
- `asyncpg` uses `?ssl=require` not `?sslmode=require` (psycopg2 convention)
- `async with AsyncSessionLocal() as session` already calls `close()` — no `finally: session.close()` needed
- `mock_db` fixture uses `yield` — annotate as `Generator[..., None, None]` or just drop the annotation (ANN suppressed in test files)
- `NotFoundError` needs HTTP 404 not 500 — use `_STATUS_MAP` dispatch in exception handler
- `raise HTTPException(...) from None` discards exception chain — use `from exc` instead

**Results:**
- **Tests:** 65 unit tests + 3 integration tests passing; `pytest -m "not integration"` deselects DB tests
- **Coverage:** 92% overall
- **Tools:** ruff, mypy, pyright all clean
- **Commands:**
  - Unit tests: `uv run pytest -v -m "not integration"`
  - Integration tests (needs Docker): `uv run pytest -v -m integration`
  - Alembic migrations: `uv run alembic upgrade head`
  - Docker: `/Applications/Docker.app/Contents/Resources/bin/docker compose up -d`

### 19. Shared Infrastructure for Cross-Feature Utilities
- Reference: `.claude/external_docs/vertical-slice-architecture-setup-guide.md`
- TDD workflow: tests written first (RED), watched fail, then implemented (GREEN)

**New files:**
- `app/shared/__init__.py` — package marker
- `app/shared/models.py` — `TimestampMixin` with `created_at`/`updated_at` via `@declared_attr`; all future models inherit this
- `app/shared/schemas.py` — `PaginationParams` (page/page_size/offset), `PaginatedResponse[T]` (generic, total_pages computed), `ErrorResponse`
- `app/shared/utils.py` — `utcnow()` (timezone-aware), `format_iso(dt)` (ISO 8601)
- `app/shared/tests/__init__.py` — package marker
- `app/shared/tests/test_models.py` — 3 tests (column presence, DateTime type)
- `app/shared/tests/test_schemas.py` — 8 tests (defaults, validation, offset, total_pages, ErrorResponse)
- `app/shared/tests/test_utils.py` — 2 tests (timezone-aware, ISO format)

**Gotchas:**
- `UP046` (Generic[T] → type params) suppressed with `# noqa: UP046` on `PaginatedResponse` — pydantic's documented Generic pattern; PEP 695 syntax untested with pydantic
- `N805` suppressed on `@declared_attr` methods — `cls` is correct convention for SQLAlchemy mixins
- `DeclarativeBase` was accidentally imported in models.py — removed (unused)

**Results:**
- **Tests:** 13 new tests; 78 unit + 3 integration all passing
- **Coverage:** 93% overall
- **Tools:** ruff, mypy, pyright all clean
- **Commit:** `80c4813 feat: add shared infrastructure for cross-feature utilities`

### 20. Diff Against `fastapi-starter-for-ai-coding`
- Ran `diff -rq` between `/Users/jsr/Workspace/Dynamous/fastapi-starter-for-ai-coding` and current project
- Excluded: `*.pyc`, `__pycache__`, `.venv`, `.git`, `.env`, `*.lock`, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `.pyright`, `htmlcov`, `.coverage`

**Only in `fastapi-starter` (reference has, current project lacks):**
- `.claude/commands/check-ingore-comments.md` — custom slash command for ignore comment audit
- `.claude/commands/validate.md` — custom slash command for full project validation
- `alembic/versions/e4a05b88d90b_initial.py` — a committed initial migration file
- `app/shared/tests/conftest.py` — shared test conftest (not present here)
- `docs/logging-standard.md` — structlog standards doc
- `docs/mypy-standard.md` — mypy standards doc
- `docs/pyright-standard.md` — pyright standards doc
- `docs/pytest-standard.md` — pytest standards doc
- `docs/ruff-standard.md` — ruff standards doc

**Only in current project (current has, `fastapi-starter` lacks):**
- `.claude/commands/create-prompt.md` — create-prompt slash command
- `.claude/external_docs/` — reference guides (ai-coding guide, vertical slice guide)
- `.claude/reports/` — ignore comment audit report
- `.claude/settings.local.json` — local Claude settings
- `.firecrawl/` — firecrawl cache
- `docs/plans/` — design and implementation plan docs
- `main.py` — root-level type-checking demo file
- `setup-prompts.md`, `summary.md`, `notestodo.md`, `steps and notes.md` — session scaffolding
- `tests/` — root-level test suite

**Files present in both but with content differences:**
- All `app/core/` source and test files
- All `app/shared/` source and test files
- `app/main.py`, `app/tests/conftest.py`, `app/tests/test_*.py`
- `pyproject.toml`, `Dockerfile`, `docker-compose.yml`, `alembic/env.py`, `alembic.ini`
- `.dockerignore`, `.env.example`, `.gitignore`, `CLAUDE.md`, `README.md`
- `.claude/commands/commit.md`

**Summary:** `fastapi-starter` is a cleaner reference template — it has standards docs, a committed initial Alembic migration, and a shared test conftest. Current project has more session scaffolding (summary, setup-prompts, plans) and external docs that wouldn't belong in a published template.

### 21. Deep Diff Against `fastapi-starter-for-ai-coding`
- Ran `diff -r` between `/Users/jsr/Workspace/Dynamous/fastapi-starter-for-ai-coding` (reference) and current project
- Findings grouped by file below. `<` = reference only, `>` = current only

#### `pyproject.toml`
- **Versions:** Reference has older pins (fastapi 0.120, pytest 8.4, ruff 0.14); current is newer
- **Ruff line-length:** Reference 100; current 88
- **Ruff rules:** Reference adds `DTZ`, `ARG`, `PTH`; current adds `N`, `A`, `SIM`; current adds `fixable = ["ALL"]`
- **Ruff per-file-ignores:** Reference suppresses `B008` globally for `health.py`; current uses inline `# noqa: B008`; current adds `alembic/**` group
- **Mypy:** Reference omits `warn_unreachable`, `strict_bytes`, AI output flags; current has all of these
- **Pyright:** Reference is minimal strict; current adds `strictListInference/DictionaryInference/SetInference`, `disableBytesTypePromotions`, opt-in rules (`reportImportCycles`, `reportUnreachable`, etc.)
- **Pytest:** Reference has no `addopts` (no auto coverage); current has `--tb=short -v --cov --cov-report=term-missing` + `[tool.coverage.*]` sections
- **Mypy overrides:** Reference targets `*.tests.*` / `test_*`; current is more specific (`tests.*`, `app.core.tests.*`, `app.tests.*`)

#### `Dockerfile`
- **Builder base:** Reference uses `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` (uv image with Python); current uses `python:3.12-slim-bookworm` + copies uv binary from distroless
- **Dep install:** Reference does `COPY` then install; current uses `--mount=type=bind` (better layer caching, no copy needed)
- **Project install:** Reference uses `--no-editable`; current omits
- **Runtime COPY:** Reference copies entire `.`; current copies only `/app/app` (tighter image)

#### `docker-compose.yml`
- **app service:** Reference adds `restart: unless-stopped`; current omits
- **build shorthand:** Reference uses full `build: context/dockerfile` block; current uses `build: .`
- **Volume syntax:** Reference `postgres_data:` (bare); current `postgres_data: {}` (explicit)
- **Reference has extensive commented-out dev patterns** (watch mode, health check template); current is lean

#### `alembic/env.py`
- **Engine creation:** Reference uses `async_engine_from_config()` (reads from ini); current uses `create_async_engine(_settings.database_url)` directly — simpler
- **Settings variable:** Reference uses `settings`; current uses `_settings` (private convention)

#### `CLAUDE.md`
- **Major difference:** Reference is a full developer handbook — KISS/YAGNI principles, vertical slice structure, DB patterns, logging taxonomy, docstring standards, agent tool docstring guidelines, feature creation workflow
- **Current:** Minimal — just commands and project structure

#### `app/main.py`
- **lifespan type:** Reference `AsyncIterator[None]`; current `AsyncGenerator[None, None]`
- **Log events:** Reference `application.lifecycle_started/stopped`, `database.connection_initialized`; current `application.startup/shutdown`, `database.connection.initialized/closed`
- **Root endpoint name:** Reference `read_root()`; current `root()`

#### `app/core/config.py`
- **`_CommaFallbackEnvSource`:** Present in current; **absent in reference** — reference relies on pydantic-settings JSON parsing only for list fields
- **`extra="ignore"`:** Reference has it; current omits

#### `app/core/database.py`
- **Session factory:** Reference explicitly sets `class_=AsyncSession`, `autocommit=False`, `autoflush=False`; current uses defaults
- **`get_db()`:** Reference wraps in `try/finally: await session.close()`; current omits (context manager handles it)

#### `app/core/exceptions.py`
- **`_STATUS_MAP`:** Present in current for type-exact dispatch; **absent in reference** — reference uses `isinstance` chain
- **Handler registration:** Reference registers all 3 types with `cast(Any, handler)`; current registers only `DatabaseError` (subtypes matched via `_STATUS_MAP`)
- **Logger fields:** Reference uses `extra={"error_type": ..., "error_message": ...}`; current uses flat kwargs

#### `app/core/health.py`
- **Function names:** Reference `health_check` / `database_health_check` / `readiness_check`; current `health` / `health_db` / `health_ready`
- **`health_ready`:** Reference injects settings via local call; current injects as `Depends(get_settings)`
- **Status codes:** Reference uses `status.HTTP_503_SERVICE_UNAVAILABLE`; current uses bare `503`

#### `app/core/logging.py`
- **`set_request_id`:** Reference `if not request_id:`; current `if request_id is not None:` (more precise — allows empty string)
- **`wrapper_class`:** Reference `make_filtering_bound_logger(level_int)`; current `structlog.stdlib.BoundLogger`
- **`cache_logger_on_first_use`:** Reference `True`; current `False` (required for test isolation)
- **Processors:** Reference includes `merge_contextvars`, `format_exc_info`; current uses `ExceptionRenderer()` instead
- **`get_logger` return type:** Reference `WrappedLogger`; current typed `structlog.stdlib.BoundLogger` (via `.bind()`)

#### `app/core/middleware.py`
- **Timing:** Reference `time.time()`; current `time.perf_counter()` (higher precision)
- **Log event names:** Reference `request.http_received/completed/failed`; current `request.started/completed/failed`
- **`call_next` type:** Reference `Callable[[Request], Awaitable[Response]]`; current `RequestResponseEndpoint`
- **pyright ignores:** Reference has `# pyright: ignore` on two lines; current is clean

#### `app/shared/models.py`
- **Decorator:** Reference `@declared_attr.directive`; current `@declared_attr`
- **Column type:** Reference `DateTime(timezone=True)`; current `sa.DateTime` (no tz param)
- **`utcnow` location:** Reference defines inline in models.py; current imports from `app.shared.utils`
- **MRO order:** Reference `(Base, TimestampMixin)`; current `(TimestampMixin, Base)`

#### `app/shared/schemas.py`
- **Generic syntax:** Reference uses PEP 695 `class PaginatedResponse[T](BaseModel):`; current uses `Generic[T]` + `# noqa: UP046`
- **`total_pages` edge case:** Reference returns `0` when `total == 0`; current returns `0` when `page_size == 0`

#### `app/shared/utils.py`
- Functionally identical — reference adds Google-style docstrings with examples; current has no docstrings

#### `app/tests/conftest.py`
- **Engine config:** Reference adds `pool_pre_ping`, `pool_size`, `max_overflow`; current is minimal
- **Session factory:** Reference passes `class_=AsyncSession`, `autocommit`, `autoflush`; current uses just `expire_on_commit=False`
- **Rollback:** Current adds `await session.rollback()` after yield; reference omits

#### `app/shared/tests/test_models.py`
- **Reference has 4 integration tests** (live DB): timestamps set on creation, `updated_at` changes on update, timezone-aware — using actual DB writes
- **Current has 3 unit tests** (no DB): column presence and DateTime type — using SQLAlchemy mapper introspection only

## TODO
## Personal TODO
- something to include later, first do PRD, then finalize the architecture and tech stack and then setup the project template
- When finalize the template - ask AI, what tools I can / should use, the external documentation for it and then create the "prompt" to setup the tool/framework, 
- Review all the prompts and see any improvemnet are needed on the specific prompts.
- Also review the /create-prompt command and see if that needs to be reviewed
- Also checkout the create-skill skill to create these commands/skills
