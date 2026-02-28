# Database Infrastructure Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a provider-agnostic PostgreSQL async layer (SQLAlchemy + asyncpg), health check endpoints, Alembic migrations, and full test coverage to the existing FastAPI template.

**Architecture:** All new infrastructure lives in `app/core/` (database.py, exceptions.py, health.py). Tests use `app.dependency_overrides` to mock the DB session for unit tests; a separate `@pytest.mark.integration` suite tests against a real database. Alembic is configured async-native, reading its URL from settings, not `alembic.ini`.

**Tech Stack:** SQLAlchemy 2.x async, asyncpg, Alembic, pytest fixtures with dependency injection overrides

---

## Task 1: Install dependencies and update pyproject.toml

**Files:**
- Modify: `pyproject.toml`

**Step 1: Install production dependencies**

```bash
uv add "sqlalchemy[asyncio]" asyncpg alembic
```

Expected: `pyproject.toml` updated with sqlalchemy, asyncpg, alembic in `[project] dependencies`.

**Step 2: Verify dev deps already present**

```bash
uv run pytest --version && uv run python -c "import httpx; print('ok')"
```

Expected: Both commands succeed. If httpx is missing: `uv add --dev httpx`.

**Step 3: Add pytest integration marker and alembic ruff excludes to pyproject.toml**

In `[tool.pytest.ini_options]`, add `markers`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests", "app"]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
asyncio_default_test_loop_scope = "function"
addopts = "--tb=short -v --cov --cov-report=term-missing"
markers = [
    "integration: marks tests requiring real database (deselect with '-m \"not integration\"')",
]
```

In `[tool.ruff.lint.per-file-ignores]`, add alembic exception:

```toml
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "ANN"]
"app/**/tests/**/*.py" = ["S101", "ANN"]
"__init__.py" = ["F401"]
"alembic/**/*.py" = ["ANN", "N", "UP", "E402"]
```

In `[tool.mypy]`, add exclude:

```toml
[tool.mypy]
python_version = "3.12"
exclude = ["alembic/"]
# ... rest unchanged
```

In `[tool.pyright]`, update exclude list:

```toml
exclude = ["**/__pycache__", ".venv", ".mypy_cache", ".firecrawl", "alembic"]
```

**Step 4: Verify ruff is clean**

```bash
uv run ruff check .
```

Expected: No errors.

**Step 5: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: install sqlalchemy, asyncpg, alembic; add integration marker"
```

---

## Task 2: Create .env and update .env.example

**Files:**
- Modify: `.env.example`
- Create: `.env`

**Step 1: Update .env.example with database section**

Replace `.env.example` with:

```ini
# =============================================================================
# Application Configuration
# =============================================================================

# Application
APP_NAME=Obsidian Agent Project
VERSION=0.1.0
ENVIRONMENT=development
LOG_LEVEL=INFO
API_PREFIX=/api

# CORS - allowed origins for cross-origin requests
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8123

# =============================================================================
# Database Configuration
# =============================================================================

# Local PostgreSQL (direct)
# DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/mydb

# Docker Compose — port 5433 on host avoids conflicts with local PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/obsidian_db

# Supabase (Session Pooler)
# DATABASE_URL=postgresql+asyncpg://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres

# Neon (requires sslmode=require)
# DATABASE_URL=postgresql+asyncpg://[user]:[password]@[host].neon.tech/[dbname]?sslmode=require

# Railway
# DATABASE_URL=postgresql+asyncpg://[user]:[password]@[host].railway.app:5432/[dbname]
```

**Step 2: Create .env for local development**

Create `.env` with the Docker URL (port 5433 to avoid conflicts with local PostgreSQL):

```ini
# Local development — .env is gitignored
ENVIRONMENT=development
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/obsidian_db
```

**Step 3: Verify .env is gitignored**

```bash
git check-ignore -v .env
```

Expected: `.gitignore:5:.env    .env` (already in .gitignore from earlier steps).

**Step 4: Commit**

```bash
git add .env.example
git commit -m "docs: add database section to .env.example"
```

---

## Task 3: Add database_url to Settings

**Files:**
- Modify: `app/core/config.py`
- Test: `app/core/tests/test_config.py`

**Step 1: Write a failing test for database_url**

Add to `app/core/tests/test_config.py`:

```python
def test_database_url_is_read_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/testdb")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.database_url == "postgresql+asyncpg://user:pass@localhost/testdb"
    get_settings.cache_clear()
```

Also add `from app.core.config import get_settings` if not already imported.

**Step 2: Run test to verify it fails**

```bash
uv run pytest app/core/tests/test_config.py::test_database_url_is_read_from_env -v
```

Expected: FAIL — `Settings` has no field `database_url`.

**Step 3: Add database_url to Settings**

In `app/core/config.py`, add after `api_prefix`:

```python
    # Database
    database_url: str
```

Full updated `Settings` class fields section:

```python
    # Application
    app_name: str = "Obsidian Agent Project"
    version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api"

    # CORS — allowed origins for cross-origin requests
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8123",
    ]

    # Database
    database_url: str
```

**Step 4: Run test to verify it passes**

```bash
uv run pytest app/core/tests/test_config.py -v
```

Expected: All config tests PASS (7 total).

**Step 5: Run full lint + type check**

```bash
uv run ruff check . && uv run mypy app/ && uv run pyright app/
```

Expected: All clean.

**Step 6: Commit**

```bash
git add app/core/config.py app/core/tests/test_config.py
git commit -m "feat: add database_url field to Settings"
```

---

## Task 4: Create app/core/database.py (TDD)

**Files:**
- Create: `app/core/tests/test_database.py`
- Create: `app/core/database.py`

**Step 1: Write failing tests**

Create `app/core/tests/test_database.py`:

```python
"""Tests for app/core/database.py."""

from __future__ import annotations

import inspect
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.core import database as db_module


async def test_engine_is_not_none() -> None:
    assert db_module.engine is not None


async def test_engine_is_async_engine() -> None:
    assert isinstance(db_module.engine, AsyncEngine)


async def test_base_metadata_is_accessible() -> None:
    assert db_module.Base.metadata is not None


async def test_get_db_is_async_generator() -> None:
    gen = db_module.get_db()
    assert inspect.isasyncgen(gen)
    await gen.aclose()


async def test_get_db_yields_async_session() -> None:
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.close = AsyncMock()

    async def fake_session_cm() -> AsyncSession:
        return mock_session

    with patch.object(
        db_module.AsyncSessionLocal,
        "__call__",
        return_value=_make_async_context_manager(mock_session),
    ):
        gen = db_module.get_db()
        session = await gen.__anext__()
        assert session is mock_session
        await gen.aclose()


def _make_async_context_manager(value: AsyncSession) -> object:
    """Return an object usable as `async with ... as value`."""

    class _CM:
        async def __aenter__(self) -> AsyncSession:
            return value

        async def __aexit__(self, *args: object) -> None:
            pass

    return _CM()
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest app/core/tests/test_database.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'app.core.database'`.

**Step 3: Create app/core/database.py**

```python
"""Async SQLAlchemy database engine, session factory, and declarative base.

Access the database in route handlers via the get_db() dependency:

    from app.core.database import get_db
    from fastapi import Depends

    async def my_route(db: AsyncSession = Depends(get_db)) -> ...:
        ...
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

_settings = get_settings()

engine = create_async_engine(
    _settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=_settings.environment == "development",
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session, closing it on exit."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest app/core/tests/test_database.py -v
```

Expected: 5 tests PASS.

**Step 5: Run lint + type check**

```bash
uv run ruff check . && uv run mypy app/ && uv run pyright app/
```

Expected: All clean.

**Step 6: Commit**

```bash
git add app/core/database.py app/core/tests/test_database.py
git commit -m "feat: add async SQLAlchemy engine, session factory, and Base"
```

---

## Task 5: Create app/core/exceptions.py (TDD)

**Files:**
- Create: `app/core/tests/test_exceptions.py`
- Create: `app/core/exceptions.py`

**Step 1: Write failing tests**

Create `app/core/tests/test_exceptions.py`:

```python
"""Tests for app/core/exceptions.py."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from fastapi import Request

from app.core.exceptions import (
    DatabaseError,
    NotFoundError,
    ValidationError,
    database_exception_handler,
)


async def test_database_error_is_exception() -> None:
    err = DatabaseError("db failure")
    assert isinstance(err, Exception)
    assert str(err) == "db failure"


async def test_not_found_error_is_database_error() -> None:
    err = NotFoundError("item 42 not found")
    assert isinstance(err, DatabaseError)
    assert isinstance(err, Exception)


async def test_validation_error_is_database_error() -> None:
    err = ValidationError("field required")
    assert isinstance(err, DatabaseError)


async def test_exception_handler_returns_json_with_error_and_type() -> None:
    request = MagicMock(spec=Request)
    request.url.path = "/test"
    exc = DatabaseError("connection timeout")

    with patch("app.core.exceptions.logger"):
        response = await database_exception_handler(request, exc)

    body = json.loads(response.body)
    assert body["error"] == "connection timeout"
    assert body["type"] == "DatabaseError"
    assert response.status_code == 500


async def test_exception_handler_logs_with_exc_info() -> None:
    request = MagicMock(spec=Request)
    request.url.path = "/test"
    exc = NotFoundError("record missing")

    with patch("app.core.exceptions.logger") as mock_logger:
        await database_exception_handler(request, exc)

    mock_logger.error.assert_called_once()
    call_kwargs = mock_logger.error.call_args.kwargs
    assert call_kwargs.get("exc_info") is True
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest app/core/tests/test_exceptions.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'app.core.exceptions'`.

**Step 3: Create app/core/exceptions.py**

```python
"""Custom exception classes and FastAPI exception handlers.

Usage in route handlers:

    from app.core.exceptions import NotFoundError
    raise NotFoundError("item not found")

Register with app via setup_exception_handlers(app) in app/main.py.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger("app.core.exceptions")


class DatabaseError(Exception):
    """Base exception for all database-related errors."""


class NotFoundError(DatabaseError):
    """Raised when a requested resource does not exist."""


class ValidationError(DatabaseError):
    """Raised when input validation fails before a database operation."""


async def database_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Return a structured JSON error response for database exceptions."""
    logger.error(
        "database.error",
        error=str(exc),
        exc_type=type(exc).__name__,
        path=request.url.path,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "type": type(exc).__name__},
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Register database exception handlers on the FastAPI application."""
    app.add_exception_handler(DatabaseError, database_exception_handler)
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest app/core/tests/test_exceptions.py -v
```

Expected: 5 tests PASS.

**Step 5: Run lint + type check**

```bash
uv run ruff check . && uv run mypy app/ && uv run pyright app/
```

Expected: All clean.

**Step 6: Commit**

```bash
git add app/core/exceptions.py app/core/tests/test_exceptions.py
git commit -m "feat: add DatabaseError hierarchy and FastAPI exception handlers"
```

---

## Task 6: Create app/core/health.py (TDD)

**Files:**
- Create: `app/core/tests/test_health.py`
- Create: `app/core/health.py`

**Step 1: Write failing tests**

Create `app/core/tests/test_health.py`:

```python
"""Tests for health check endpoints."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.main import app


@pytest.fixture
def mock_db(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    """Override get_db dependency with a mock AsyncSession."""
    session = AsyncMock(spec=AsyncSession)

    async def override() -> object:
        yield session

    app.dependency_overrides[get_db] = override
    yield session
    app.dependency_overrides.clear()


async def test_health_returns_200_without_db() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "api"


async def test_health_db_returns_200_when_connected(mock_db: AsyncMock) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "database"
    assert data["provider"] == "postgresql"


async def test_health_db_returns_503_when_db_fails(mock_db: AsyncMock) -> None:
    mock_db.execute.side_effect = Exception("connection refused")
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health/db")
    assert response.status_code == 503


async def test_health_ready_returns_200_when_ready(mock_db: AsyncMock) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "environment" in data
    assert data["database"] == "connected"


async def test_health_ready_returns_503_when_db_fails(mock_db: AsyncMock) -> None:
    mock_db.execute.side_effect = Exception("connection refused")
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health/ready")
    assert response.status_code == 503
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest app/core/tests/test_health.py -v
```

Expected: FAIL — health endpoints don't exist yet, all return 404.

**Step 3: Create app/core/health.py**

```python
"""Health check endpoints.

Endpoints are registered WITHOUT a prefix so they live at the root path:
    GET /health       — API process is running
    GET /health/db    — database connection is available
    GET /health/ready — all dependencies healthy and ready for traffic
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.core.logging import get_logger

logger = get_logger("app.core.health")

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Confirm the API process is running."""
    return {"status": "healthy", "service": "api"}


@router.get("/health/db")
async def health_db(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Confirm the database connection is available."""
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        logger.error("database.health_check_failed", exc_info=True)
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "healthy", "service": "database", "provider": "postgresql"}


@router.get("/health/ready")
async def health_ready(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    """Confirm all dependencies are ready for traffic."""
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        logger.error("database.health_check_failed", exc_info=True)
        raise HTTPException(status_code=503, detail="Database not ready")
    return {
        "status": "ready",
        "environment": settings.environment,
        "database": "connected",
    }
```

**Step 4: Run tests to verify they fail** (health router not yet registered in main.py)

```bash
uv run pytest app/core/tests/test_health.py -v
```

Expected: FAIL — 404 responses. This is correct; Task 7 wires it in.

**Step 5: Run lint + type check on health.py**

```bash
uv run ruff check app/core/health.py && uv run mypy app/core/health.py && uv run pyright app/core/health.py
```

Expected: All clean.

**Step 6: Commit health.py and tests (before wiring into main)**

```bash
git add app/core/health.py app/core/tests/test_health.py
git commit -m "feat: add health check router (GET /health, /health/db, /health/ready)"
```

---

## Task 7: Update app/main.py

**Files:**
- Modify: `app/main.py`

**Step 1: Update app/main.py**

Replace the full file with:

```python
"""FastAPI application entry point.

Run with: uv run uvicorn app.main:app --reload --port 8123
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.core.config import get_settings
from app.core.database import engine
from app.core.exceptions import setup_exception_handlers
from app.core.health import router as health_router
from app.core.logging import get_logger, setup_logging
from app.core.middleware import setup_middleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Configure logging and announce startup/shutdown."""
    setup_logging(log_level=settings.log_level)
    logger = get_logger("app.main")
    logger.info("application.startup", environment=settings.environment)
    logger.info("database.connection.initialized")
    yield
    await engine.dispose()
    logger.info("database.connection.closed")
    logger.info("application.shutdown")


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan,
)

setup_middleware(app)
setup_exception_handlers(app)
app.include_router(health_router)


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint — confirms the API is running."""
    return {
        "message": settings.app_name,
        "version": settings.version,
        "docs": "/docs",
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8123, reload=True)  # noqa: S104
```

**Step 2: Run all tests to verify health tests now pass**

```bash
uv run pytest -v -m "not integration"
```

Expected: All unit tests pass including the 5 health tests. Total ≥ 53 tests.

**Step 3: Run lint + type check**

```bash
uv run ruff check . && uv run mypy app/ && uv run pyright app/
```

Expected: All clean.

**Step 4: Commit**

```bash
git add app/main.py
git commit -m "feat: wire health router, exception handlers, and engine dispose into main"
```

---

## Task 8: Update docker-compose.yml with PostgreSQL

**Files:**
- Modify: `docker-compose.yml`

**Step 1: Replace docker-compose.yml**

```yaml
services:
  db:
    image: postgres:18-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: obsidian_db
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  app:
    build: .
    ports:
      - "8123:8123"
    volumes:
      # Mount project source for live code changes in development
      - .:/app
      # Exclude .venv so the container uses its own installed packages
      - /app/.venv
    env_file:
      - path: .env
        required: false
    environment:
      - PYTHONUNBUFFERED=1
      # Override for Docker networking (app → db service, not localhost)
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/obsidian_db
    depends_on:
      db:
        condition: service_healthy

volumes:
  postgres_data: {}
```

**Step 2: Commit**

```bash
git add docker-compose.yml
git commit -m "feat: add PostgreSQL service to docker-compose with health check"
```

---

## Task 9: Initialize and configure Alembic

**Files:**
- Create: `alembic/` (via `alembic init`)
- Modify: `alembic/env.py`
- Modify: `alembic.ini`

**Step 1: Initialize Alembic**

```bash
uv run alembic init alembic
```

Expected: Creates `alembic/`, `alembic/env.py`, `alembic/script.py.mako`, `alembic/versions/`, and `alembic.ini`.

**Step 2: Edit alembic.ini — comment out sqlalchemy.url**

Find this line in `alembic.ini`:

```ini
sqlalchemy.url = driver://user:pass@localhost/dbname
```

Replace with:

```ini
# sqlalchemy.url is set programmatically from settings.database_url in env.py
# sqlalchemy.url = driver://user:pass@localhost/dbname
```

**Step 3: Replace alembic/env.py with async-native version**

```python
"""Alembic environment configuration — async-native SQLAlchemy setup."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from app.core.database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

_settings = get_settings()
config.set_main_option("sqlalchemy.url", _settings.database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations using a live synchronous connection."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create async engine and run migrations via run_sync."""
    connectable = create_async_engine(_settings.database_url)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online migration mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Step 4: Update .gitignore to ignore alembic pycache**

The existing `.gitignore` already has `__pycache__/`, which covers `alembic/versions/__pycache__/`. Verify:

```bash
git check-ignore -v alembic/versions/__pycache__
```

Expected: Matched by `__pycache__/` rule (or no output if pycache doesn't exist yet, which is fine).

**Step 5: Verify alembic config works**

```bash
uv run alembic current
```

Expected: Either shows current revision (none if no migrations yet) or an error about DB connection. If you get a DB connection error, that's expected if no PostgreSQL is running locally — the alembic config is correct.

If you have Docker running, start it first:

```bash
/Applications/Docker.app/Contents/Resources/bin/docker compose up -d db
uv run alembic current
```

Expected: `INFO  [alembic.runtime.migration] Context impl PostgreSQLImpl.` then the current revision (empty).

**Step 6: Commit**

```bash
git add alembic/ alembic.ini
git commit -m "feat: initialize Alembic with async-native PostgreSQL configuration"
```

---

## Task 10: Integration test fixtures and test_database_integration.py

**Files:**
- Create: `app/tests/conftest.py`
- Create: `app/tests/test_database_integration.py`

**Step 1: Create app/tests/conftest.py**

```python
"""Shared fixtures for app/tests/ integration tests.

These fixtures require a real PostgreSQL database.
Run integration tests with: pytest -v -m integration
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings


@pytest.fixture
async def test_db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create a fresh async engine for the test, dispose on teardown."""
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_db_session(
    test_db_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh AsyncSession per test, rolling back on teardown."""
    session_factory = async_sessionmaker(test_db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()
```

**Step 2: Create app/tests/test_database_integration.py**

```python
"""Integration tests for database connectivity.

Requires a real PostgreSQL database at settings.database_url.
Run with: pytest -v -m integration
Skip with: pytest -v -m "not integration"
"""

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

pytestmark = pytest.mark.integration


async def test_database_connection(test_db_session: AsyncSession) -> None:
    """Verify the database accepts queries."""
    result = await test_db_session.execute(text("SELECT 1"))
    row = result.fetchone()
    assert row is not None
    assert row[0] == 1


async def test_session_executes_queries(test_db_session: AsyncSession) -> None:
    """Verify session can run multiple queries."""
    result = await test_db_session.execute(text("SELECT current_database()"))
    row = result.fetchone()
    assert row is not None
    assert isinstance(row[0], str)


async def test_base_metadata_is_configured(test_db_session: AsyncSession) -> None:
    """Verify Base.metadata is accessible (needed for schema operations)."""
    assert Base.metadata is not None
```

**Step 3: Run unit tests (must still pass without DB)**

```bash
uv run pytest -v -m "not integration"
```

Expected: All unit tests pass. Integration tests skipped.

**Step 4: Run integration tests (requires PostgreSQL)**

If Docker is running:

```bash
/Applications/Docker.app/Contents/Resources/bin/docker compose up -d db
uv run pytest -v -m integration
```

Expected: 3 integration tests PASS.

**Step 5: Run full type check**

```bash
uv run ruff check . && uv run mypy app/ && uv run pyright app/
```

Expected: All clean.

**Step 6: Commit**

```bash
git add app/tests/conftest.py app/tests/test_database_integration.py
git commit -m "feat: add integration test fixtures and database integration tests"
```

---

## Task 11: Final validation

**Step 1: Run full unit test suite**

```bash
uv run pytest -v -m "not integration"
```

Expected: ≥ 53 tests passing (48 existing + 5 database + 5 exceptions + 5 health). Coverage > 80%.

**Step 2: Run full lint + type check**

```bash
uv run ruff check . && uv run mypy app/ && uv run pyright app/
```

Expected: 0 errors on all three tools.

**Step 3: Run integration tests (Docker required)**

```bash
/Applications/Docker.app/Contents/Resources/bin/docker compose up -d db && sleep 3
uv run pytest -v -m integration
```

Expected: 3 integration tests PASS.

**Step 4: Verify health endpoints locally**

```bash
# Start server (requires .env with DATABASE_URL)
uv run uvicorn app.main:app --port 8123 &
sleep 2
curl -s http://localhost:8123/health | python3 -m json.tool
curl -s http://localhost:8123/health/db | python3 -m json.tool
curl -s http://localhost:8123/health/ready | python3 -m json.tool
kill %1
```

Expected:
- `/health` → `{"status": "healthy", "service": "api"}`
- `/health/db` → `{"status": "healthy", "service": "database", "provider": "postgresql"}`
- `/health/ready` → `{"status": "ready", "environment": "development", "database": "connected"}`

**Step 5: Final commit if anything was adjusted**

```bash
git add -p  # stage any remaining changes
git commit -m "chore: database infrastructure complete — all tests passing"
```

---

## Summary

| Task | Files | Tests added |
|------|-------|-------------|
| 1 | pyproject.toml, uv.lock | — |
| 2 | .env.example, .env | — |
| 3 | config.py, test_config.py | +1 |
| 4 | database.py, test_database.py | +5 |
| 5 | exceptions.py, test_exceptions.py | +5 |
| 6 | health.py, test_health.py | +5 |
| 7 | main.py | 5 activated |
| 8 | docker-compose.yml | — |
| 9 | alembic/, alembic.ini | — |
| 10 | conftest.py, test_database_integration.py | +3 (integration) |

**Expected totals:** ≥ 53 unit tests + 3 integration tests, ruff/mypy/pyright clean, >80% coverage
