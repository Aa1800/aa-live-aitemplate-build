# Database Infrastructure Design

**Date:** 2026-02-27
**Status:** Approved
**Scope:** PostgreSQL async database layer, health checks, Alembic migrations

---

## Overview

Add a provider-agnostic PostgreSQL layer to the existing FastAPI + structlog template using SQLAlchemy async, Alembic for migrations, and FastAPI health endpoints. No feature slices yet — all new code lives in `app/core/`.

---

## Architecture

```
app/
├── core/
│   ├── config.py          # update: add database_url field
│   ├── database.py        # NEW: engine, session factory, Base, get_db()
│   ├── exceptions.py      # NEW: DatabaseError hierarchy + FastAPI handlers
│   ├── health.py          # NEW: /health, /health/db, /health/ready router
│   ├── middleware.py      # unchanged
│   └── logging.py         # unchanged
├── main.py                # update: health router, exception handlers, engine.dispose()
└── tests/
    └── conftest.py        # NEW: test_db_engine + test_db_session fixtures
alembic/                   # NEW: migration environment (async-native)
.env                       # NEW: local dev secrets (gitignored)
```

---

## Component Design

### `app/core/database.py`
- Engine created at module import (required for Alembic compatibility)
- Pool: `pool_size=5`, `max_overflow=10`, `pool_pre_ping=True`
- `echo=True` only when `settings.environment == "development"`
- `AsyncSessionLocal` via `async_sessionmaker(expire_on_commit=False)`
- `Base` extends `DeclarativeBase` for model definitions
- `get_db()` async generator: opens session, yields, closes in finally

### `app/core/exceptions.py`
- Three-tier hierarchy: `DatabaseError(Exception)` → `NotFoundError`, `ValidationError`
- FastAPI exception handlers return `{"error": str(exc), "type": type(exc).__name__}`
- `setup_exception_handlers(app)` registers all handlers on the FastAPI instance
- Handlers log errors via structlog before returning JSON

### `app/core/health.py`
- `APIRouter(tags=["health"])` with no prefix (health at root, not `/api`)
- `GET /health` — no dependencies, returns `{"status": "healthy", "service": "api"}`
- `GET /health/db` — `Depends(get_db)`, executes `SELECT 1`, 503 on failure
- `GET /health/ready` — `Depends(get_db)` + `get_settings`, checks DB + config, 503 on failure

### `app/main.py` updates
- Import and register `health_router` via `app.include_router(health_router)`
- Call `setup_exception_handlers(app)` at module level
- Lifespan: log `database.connection.initialized` on startup; `await engine.dispose()` + log on shutdown

### Alembic
- Async-native: `create_async_engine` + `AsyncConnection` + `run_sync` in `env.py`
- URL sourced from `settings.database_url` — `sqlalchemy.url` line in `alembic.ini` commented out
- `target_metadata = Base.metadata` for autogenerate support

---

## Test Strategy

### Unit tests (no real DB required)
- `test_database.py`: mock `get_settings()` to inject a fake URL; test engine creation, `get_db()` lifecycle, `Base` configuration
- `test_exceptions.py`: test exception class hierarchy, handler JSON shape, logging
- `test_health.py`: full `app` instance with `app.dependency_overrides[get_db] = mock_session`; test 200 and 503 cases

### Integration tests (`@pytest.mark.integration`)
- `test_database_integration.py`: use real PostgreSQL via `test_db_session` fixture
- Run with: `pytest -v -m integration`
- Excluded from default run: `pytest -v -m "not integration"`

### Fixtures (`app/tests/conftest.py`)
- `test_db_engine`: creates fresh async engine per test
- `test_db_session`: creates fresh `AsyncSession` per test via `test_db_engine`

---

## Environment / Secrets

- `database_url: str` added to `Settings` with **no default** (required)
- `.env` file provides `DATABASE_URL` for local dev and test runs (gitignored)
- Tests rely on `.env` being present; no conftest fallback
- `.env.example` updated with examples for Docker, Supabase, Neon, Railway, local PostgreSQL

---

## Docker

- `db` service: `postgres:18-alpine`, port `5433:5432`, named volume `postgres_data`
- Health check: `pg_isready -U postgres` (5s interval, 5s timeout, 5 retries)
- `app` service: `depends_on: db: condition: service_healthy`
- App `DATABASE_URL` overridden for Docker networking: `postgresql+asyncpg://postgres:postgres@db:5432/obsidian_db`

---

## Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| `database_url` default | None (required) | Forces explicit config; `.env` provides it locally |
| Health test client | Full `app` + `dependency_overrides` | Consistent with existing test_main.py pattern |
| Alembic async | `create_async_engine` + `run_sync` | Matches runtime engine; single driver (asyncpg) |
| Integration marker | `@pytest.mark.integration` | Deselectable with `-m "not integration"` |
