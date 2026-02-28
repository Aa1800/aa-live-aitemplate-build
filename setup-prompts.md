# Setup Prompts

These prompts are extracted from `.claude/external_docs/ai-coding-project-setup-guide.md` in the order they appear and should be run.

---

## 1. Ruff Setup

```
Using the official Ruff documentation as context, let's set up Ruff for our project optimized for AI self-correction.

Documentation to read: FETCH:(https://docs.astral.sh/ruff/configuration/)
Read and understand the configuration options before continuing.

Don't set up anything beyond Ruff.

Write a simple Python script in main.py then test our Ruff setup when done.
```

---

## 2. MyPy Setup

```
Using the official MyPy documentation as context, set up MyPy for our project.

Documentation to read: FETCH:(https://mypy.readthedocs.io/en/stable/config_file.html)
Read and understand the configuration options, especially strict mode settings.

First, run:
uv add --dev mypy

Then add the MyPy configuration to pyproject.toml based on the documentation, optimized for ai coding.

When you have added the rules, modify main.py to properly test that all of our type checking rules are working as expected.

main.py is just for testing, so feel free to override anything that's there.

When done, write a short summary of what was configured and tested.
```

---

## 3. Pyright Setup

```
Using the official Pyright documentation as context, set up Pyright for our project as a second layer of type safety.

Documentation to read: FETCH:(https://github.com/microsoft/pyright/blob/main/docs/configuration.md)
Read and understand the configuration options, especially type checking modes and diagnostic rules.

First, run:
uv add --dev pyright

Then add the Pyright configuration to pyproject.toml based on the documentation. Use strict mode with all safety checks enabled.

When you have added the rules, run both MyPy and Pyright on main.py to verify both type checkers pass.

main.py is just for testing, so feel free to override anything that's there.

When done, write a short summary comparing what Pyright caught vs MyPy.
```

---

## 4. Pytest Setup

```
Using the official pytest-asyncio documentation as context, set up pytest for our project.

Documentation to read: FETCH:(https://pytest-asyncio.readthedocs.io/)
Read and understand async test setup, fixtures, and event loop configuration.

First, run:
uv add --dev pytest pytest-cov pytest-asyncio

Then create tests for main.py following best practices from the documentation.

Make sure all tests pass, and that Ruff, MyPy, and Pyright checks all pass as well.

When everything is green, run /commit to commit the changes.

Write a short summary of what was configured and tested.
output:
Summary: [short descriptive summary]
Files changed: [bullet list]
# tests passing: [bullet list]
exact commit message used:
```

---

## 5. Structured Logging Setup

```
Using this article as context, set up structured logging for our project.

Here is the article to read: .claude/external-docs/ai-coding-project-setup-guide.md
The file contains the hybrid logging pattern we need to implement.

First, run:
uv add structlog

Then create app/core/logging.py with:
- JSON output for AI-parseable logs
- Request ID correlation using context variables
- Hybrid dotted namespace pattern: domain.component.action_state
  - Format: {domain}.{component}.{action}_{state}
  - Examples: user.registration_started, database.connection_initialized
  - States: _started, _completed, _failed, _validated, _rejected
- Exception formatting with exc_info for stack traces
- See .claude/external-docs/ai-coding-project-setup-guide.md section 6 for pattern details

Create a simple example in app/main.py demonstrating the logging pattern.

Write unit tests in app/core/tests/test_logging.py

Ruff linting, MyPy, and Pyright must all pass with no errors. You can see the setup in pyproject.toml

When everything is green run /commit

When done, write a short summary of what was configured and how to use it.
output:
Summary: [short descriptive summary]
Key features: [bullet list of logging capabilities]
Usage example: [show the basic pattern]
```

---

## 6. Docker Setup

```
Using this article as context, set up Docker for our project with uv.

Here is the article to read FETCH:(https://docs.astral.sh/uv/guides/integration/docker/)
read it and fully understand it before you continue, do any additional research as needed

Create:
1. Dockerfile using multi-stage build with official uv images
   - Use python3.12-bookworm-slim as base
   - Separate dependency installation layer for caching
   - Use --no-editable for production builds
   - Include cache mounts for uv

2. .dockerignore file to exclude:
   - Virtual environments (.venv)
   - Cache directories (.mypy_cache, .ruff_cache, .pytest_cache, .pyright)
   - Python bytecode (__pycache__, *.pyc)
   - Git and environment files

3. docker-compose.yml for local development with:
   - Volume mounts for the project (excluding .venv)
   - Port mapping (8123:8123)
   - Environment variable support

Test the setup:
- Build the Docker image successfully
- Verify the image size is reasonable
- Test running the container

When done, write a short summary of the Docker setup.
output:
Summary: [short descriptive summary]
Image details: [size, base image, key optimizations]
Usage commands: [docker build, docker run, docker compose]
```

---

## 7. FastAPI + Configuration + Middleware

````
Using the vertical slice architecture guide as context, set up FastAPI with Pydantic for our project.

Context articles to read:
1. .claude/external-docs/vertical-slice-architecture-setup-guide.md
   Read the article to understand infrastructure patterns.

2. FastAPI best practices: FETCH:(https://fastapi.tiangolo.com/advanced/events/)
   Focus on lifespan events for startup/shutdown

First, install dependencies:
uv add fastapi uvicorn[standard] pydantic-settings python-dotenv

Then create these files:

1. app/core/config.py with:
   - Settings class using pydantic-settings BaseSettings
   - Fields: app_name, version, environment, log_level, api_prefix
   - CORS settings: allowed_origins (list)
   - All fields properly typed with descriptions
   - Cached get_settings() function using @lru_cache
   - Settings loaded from .env file (with required=False since it won't exist yet)
   - Example:
     ```python
     class Settings(BaseSettings):
         model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

         app_name: str = "Obsidian Agent Project"
         version: str = "0.1.0"
         environment: str = "development"
         log_level: str = "INFO"
         api_prefix: str = "/api"

         # CORS
         allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8123"]
     ```

2. app/core/middleware.py with:
   - RequestLoggingMiddleware that integrates with our existing app.core.logging
   - Sets request_id from X-Request-ID header or generates new one using set_request_id()
   - Logs "request.started" with method, path, client_host
   - Logs "request.completed" with method, path, status_code, duration_seconds
   - Logs "request.failed" with exc_info=True on exceptions
   - Adds X-Request-ID to response headers
   - setup_middleware(app) function that adds RequestLoggingMiddleware and CORS
   - Use settings.allowed_origins for CORS

3. Update app/main.py to be a FastAPI application:
   - Clean up existing example code for logging
   - Import FastAPI, setup_middleware, setup_logging, get_settings, get_logger
   - Create lifespan async context manager that:
     - Calls setup_logging(log_level=settings.log_level) on startup
     - Gets logger and logs "application.startup" with environment
     - Yields
     - Logs "application.shutdown" on shutdown
   - Create FastAPI app with lifespan, title, version from settings
   - Call setup_middleware(app)
   - Add root endpoint GET / that returns:
     {
       "message": "Obsidian Agent Project",
       "version": settings.version,
       "docs": "/docs"
     }
   - Add if __name__ == "__main__": block that runs uvicorn on port 8123

4. Create .env.example with:
   - Application settings only (no database yet - we'll add that next)
   - Clear comments explaining each setting
   - Example content:
     ```
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
     ```

5. Update pyproject.toml:
   - Change name to "VSA fastapi project"
   - Add proper description: "FastAPI + PostgreSQL starter with vertical slice architecture, optimized for AI coding"
   - Update known-first-party in ruff config: ["app"]

6. Create test files:

   app/core/tests/test_config.py:
   - Test Settings instantiation with defaults
   - Test Settings from environment variables
   - Test get_settings() caching works
   - Test allowed_origins parsing (list from string)

   app/core/tests/test_middleware.py:
   - Test RequestLoggingMiddleware generates request_id
   - Test middleware uses X-Request-ID header if provided
   - Test middleware logs request.started and request.completed
   - Test middleware logs request.failed with exc_info on exceptions
   - Test X-Request-ID appears in response headers
   - Use pytest fixtures with mock logger to verify log calls

   app/tests/test_main.py:
   - Test root endpoint returns correct JSON structure
   - Test /docs endpoint is accessible
   - Test lifespan events (startup logging)
   - Test CORS headers are present
   - Use httpx.AsyncClient for testing FastAPI endpoints
   - Mock settings if needed for consistent tests

Test requirements:

e2e testing:
- Start the app: uv run uvicorn app.main:app --reload --port 8123
- curl http://localhost:8123 and verify root endpoint returns correct JSON
- curl http://localhost:8123/docs and verify Swagger UI appears
- Check terminal logs - should see structured JSON logs with request_id
- Send request with curl -H "X-Request-ID: test-123" http://localhost:8123
  and verify logs include request_id: "test-123"

Automated testing:
- Run all tests: pytest -v
- Verify test coverage for new modules: pytest --cov=app.core --cov-report=term-missing
- All tests should pass (logging tests, config tests, middleware tests, API tests)
- All linting (ruff check .), type checking (mypy app/, pyright app/) must pass

Expected test output:
- test_config.py: ~4 tests passing (settings, defaults, caching)
- test_middleware.py: ~5 tests passing (request_id, logging, headers)
- test_main.py: ~4 tests passing (root endpoint, docs, CORS)
- Total: ~13+ tests passing
- Coverage: >80% for app/core modules

When everything is green, let the user know we are ready to commit

Output format:
Summary: [short summary of what was built]
Files created: [bullet list]
Configuration: [key settings explained]
Test results: [manual testing + linting + type checking]
````

---

## 8. Check Ignore Comments

```
Find all noqa/type:ignore comments in the codebase, investigate why they exist, and provide recommendations for resolution or justification.

Create a markdown report file (create the reports directory if not created yet): `.claude/reports/ignore-comments-report-{YYYY-MM-DD}.md`
report:

**Why it exists:**
{explanation of why the suppression was added}

**Options to resolve:**

1. {Option 1: description}
   - Effort: {Low/Medium/High}
   - Breaking: {Yes/No}
   - Impact: {description}

2. {Option 2: description}
   - Effort: {Low/Medium/High}
   - Breaking: {Yes/No}
   - Impact: {description}

**Tradeoffs:**

- {Tradeoff 1}
- {Tradeoff 2}

**Recommendation:** {Remove | Keep | Refactor}
{Justification for recommendation}

---

{Repeat for each comment}
```

---

## 9. Validate (Full Project Health Check)

```
Run comprehensive validation of the project to ensure all tests, type checks, linting, and deployments are working correctly.

Execute the following commands in sequence and report results:

## 1. Test Suite

uv run pytest -v

**Expected:** All tests pass (currently 34 tests), execution time < 1 second

## 2. Type Checking

uv run mypy app/

**Expected:** "Success: no issues found in X source files"

uv run pyright app/

**Expected:** "0 errors, 0 warnings, 0 informations"

## 3. Linting

uv run ruff check .

**Expected:** "All checks passed!"

## 4. Local Server Validation

Start the server in background:

uv run uvicorn app.main:app --host 0.0.0.0 --port 8123 &

Wait 3 seconds for startup, then test endpoints:

curl -s http://localhost:8123/ | python3 -m json.tool

**Expected:** JSON response with app name, version, and docs link

curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8123/docs

**Expected:** HTTP Status: 200

curl -s -i http://localhost:8123/ | head -10

**Expected:** Headers include `x-request-id` and status 200

Stop the server:

lsof -ti:8123 | xargs kill -9 2>/dev/null || true

## 5. Docker Deployment Validation

Build and start Docker service:

docker-compose up -d --build

**Expected:** Container builds successfully and starts

Wait 5 seconds, then verify container status:

docker-compose ps

**Expected:** Container status shows "Up"

Test Docker endpoints:

curl -s http://localhost:8123/ | python3 -m json.tool

**Expected:** Same JSON response as local server

curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8123/docs

**Expected:** HTTP Status: 200

Check Docker logs:

docker-compose logs app | tail -20

**Expected:** Structured JSON logs with request_id, startup message, request logging

Stop Docker service:

docker-compose down

## 6. Summary Report

After all validations complete, provide a summary report with:

- Total tests passed/failed
- Type checking status (mypy + pyright)
- Linting status
- Local server status
- Docker deployment status
- Any errors or warnings encountered
- Overall health assessment (PASS/FAIL)

**Format the report clearly with sections and status indicators (✅/❌)**
```

---

## 10. Database Infrastructure (PostgreSQL + Health Checks + Alembic)

````
Using the vertical slice architecture guide, set up PostgreSQL database infrastructure.

Context: READ .claude/external-docs/vertical-slice-architecture-setup-guide.md

This setup must be provider-agnostic - work with ANY PostgreSQL provider (Docker, Supabase, Neon, Railway, etc.)

First, install dependencies:
uv add sqlalchemy[asyncio] asyncpg alembic
uv add --dev pytest-asyncio httpx (if not already added)

Then create these NEW files:

1. app/core/database.py with:
   - Import create_async_engine, AsyncSession, async_sessionmaker from sqlalchemy.ext.asyncio
   - Import DeclarativeBase from sqlalchemy.orm
   - Get settings from core.config
   - Create async engine with:
     * settings.database_url
     * pool_pre_ping=True (test connections before using)
     * pool_size=5, max_overflow=10
     * echo=True if environment is "development" else False
   - Create AsyncSessionLocal using async_sessionmaker
   - Define Base class extending DeclarativeBase (for SQLAlchemy models)
   - Define async get_db() generator:
     ```python
     async def get_db() -> AsyncGenerator[AsyncSession, None]:
         async with AsyncSessionLocal() as session:
             try:
                 yield session
             finally:
                 await session.close()
     ```

2. app/core/exceptions.py (NEW file) with:
   - Custom exception classes:
     * DatabaseError(Exception) - base database exception
     * NotFoundError(DatabaseError) - resource not found
     * ValidationError(DatabaseError) - validation failed
   - Global exception handler for FastAPI:
     * async def database_exception_handler that logs errors and returns JSON
     * Returns {"error": str(exc), "type": type(exc).__name__}
   - Function to register handlers: setup_exception_handlers(app)

3. app/core/health.py (NEW file) with:
   - Import APIRouter, Depends, HTTPException from fastapi
   - Import AsyncSession and get_db from core.database
   - Import get_logger from core.logging
   - Import text from sqlalchemy
   - Create router = APIRouter(tags=["health"])
   - Three endpoints (NO prefix - health checks are typically at root):

     GET /health:
     - No dependencies
     - Returns {"status": "healthy", "service": "api"}

     GET /health/db:
     - Uses Depends(get_db)
     - Executes SELECT 1 via db.execute(text("SELECT 1"))
     - Returns {"status": "healthy", "service": "database", "provider": "postgresql"}
     - Logs errors with logger.error("database.health_check_failed", exc_info=True)
     - Raises HTTPException(503) if database fails

     GET /health/ready:
     - Uses Depends(get_db) and get_settings
     - Checks database connection
     - Returns {"status": "ready", "environment": settings.environment, "database": "connected"}
     - Raises HTTPException(503) if not ready

4. UPDATE existing app/core/config.py:
   - Add database_url field to Settings class:
     ```python
     # Database
     database_url: str
     ```

5. UPDATE existing app/main.py:
   - Import health router, database exception handlers, engine
   - Update lifespan to:
     * On startup: Log "database.connection.initialized"
     * On shutdown: Call await engine.dispose() and log "database.connection.closed"
   - Add app.include_router(health_router) (no prefix!)
   - Call setup_exception_handlers(app)

6. UPDATE existing docker-compose.yml to add PostgreSQL service:
   - Add db service using postgres:18-alpine image
   - Environment variables: POSTGRES_USER=postgres, POSTGRES_PASSWORD=postgres, POSTGRES_DB=obsidian_db
   - Port mapping: 5433:5432 (host:container - use non-standard port to avoid conflicts with local PostgreSQL)
   - Named volume: postgres_data for persistence
   - Health check: pg_isready -U postgres (interval: 5s, timeout: 5s, retries: 5)
   - App service changes:
     * Add depends_on with db service and condition: service_healthy
     * Override DATABASE_URL for Docker networking: postgresql+asyncpg://postgres:postgres@db:5432/obsidian_db
   - Add volumes section at bottom: postgres_data: {}

7. Initialize Alembic for migrations:
   - Run: alembic init alembic
   - Edit alembic/env.py to use async:
     * Import asyncio
     * Import Base from app.core.database
     * Import settings from app.core.config
     * Set target_metadata = Base.metadata
     * Set sqlalchemy.url from settings.database_url in config section
     * Convert run_migrations_online to async function
     * Use create_async_engine and AsyncConnection
   - Edit alembic.ini:
     * Comment out sqlalchemy.url line (we get it from settings)

8. UPDATE existing .env.example to add database section:
   - Add comprehensive database examples for Docker, Supabase, Neon, Railway, and local PostgreSQL

9. Create .env file for local development (gitignored):
   - Copy from .env.example
   - Use Docker connection string with port 5433
   - Set LOG_LEVEL=DEBUG for development
   - DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/obsidian_db

10. Update .gitignore:
   - Add .env (actual secrets)
   - Ensure alembic/versions/__pycache__ is ignored

11. Create test fixtures and test files:

   app/tests/conftest.py (NEW - REQUIRED):
   - test_db_engine fixture: creates fresh async engine per test
   - test_db_session fixture: creates fresh session per test using test_db_engine

   app/core/tests/test_database.py:
   - Test async engine creation
   - Test get_db() session lifecycle (creates and closes)
   - Test Base class is properly configured
   - Mock settings.database_url for isolated testing

   app/core/tests/test_exceptions.py:
   - Test DatabaseError, NotFoundError, ValidationError raise correctly
   - Test exception handler returns proper JSON structure
   - Test exception handler logs with exc_info

   app/core/tests/test_health.py:
   - Test GET /health returns 200 without database
   - Test GET /health/db returns 200 with database connected
   - Test GET /health/db returns 503 when database fails
   - Test GET /health/ready returns 200 when all dependencies healthy
   - Use pytest fixtures to override get_db dependency

   app/tests/test_database_integration.py:
   - MUST use test_db_session fixture parameter, NOT module imports
   - Test full database connection with real PostgreSQL
   - Test session lifecycle, metadata operations
   - Mark with @pytest.mark.integration

Configure pytest markers in pyproject.toml:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["app", "tests"]
markers = [
    "integration: marks tests requiring real database (deselect with '-m \"not integration\"')",
]
```

Test requirements:
- Unit tests (no database): pytest -v -m "not integration"
- Integration tests (database required): pytest -v -m integration
- Full suite: pytest -v
- All linting (ruff check ., mypy app/, pyright app/) must pass

Expected test output:
- test_database.py: ~3 tests passing
- test_exceptions.py: ~4 tests passing
- test_health.py: ~6 tests passing
- test_database_integration.py: ~3 tests passing
- Grand total: ~29+ tests passing
- Coverage: >80% for app/core modules

When everything is green, let the user know we are ready to commit

Output format:
Summary: [comprehensive summary of database infrastructure]
Files created/modified: [bullet list with descriptions]
Database features: [provider-agnostic, health checks, migrations, etc.]
Docker setup: [postgres service details]
Test results: [health endpoints, migrations, linting, type checking]
````

---

## 11. Shared Utilities & Patterns

```
Create shared infrastructure for cross-feature utilities.

Context: READ .claude/external-docs/vertical-slice-architecture-setup-guide.md

We're setting up utilities that ALL features will use:
- Database model mixins (timestamps on every table)
- API patterns (pagination on every list endpoint)
- Common response formats (consistent error/success responses)
- Utility functions (date handling, validation)

Create these files:

1. app/shared/__init__.py (empty file for package)

2. app/shared/models.py with:
   - TimestampMixin class with:
     * created_at: DateTime column with default=datetime.utcnow
     * updated_at: DateTime column with default=datetime.utcnow, onupdate=datetime.utcnow
     * Use @declared_attr for columns (SQLAlchemy mixin pattern)
   - Proper imports from sqlalchemy
   - All future models will inherit this mixin

3. app/shared/schemas.py with:
   - PaginationParams(BaseModel):
     * page: int = Field(default=1, ge=1, description="Page number")
     * page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
     * Property: offset (calculated as (page - 1) * page_size)

   - PaginatedResponse(BaseModel, Generic[T]):
     * items: List[T]
     * total: int
     * page: int
     * page_size: int
     * total_pages: int (calculated from total/page_size, rounded up)
     * Use Generic[T] for type-safe responses

   - ErrorResponse(BaseModel):
     * error: str
     * type: str
     * detail: str | None = None
     * Used by exception handlers

4. app/shared/utils.py with:
   - utcnow() -> datetime:
     * Returns datetime.now(timezone.utc)
     * Consistent timezone-aware timestamps
   - format_iso(dt: datetime) -> str:
     * Returns dt.isoformat()
     * Standard ISO 8601 formatting

5. Create comprehensive tests:

   app/shared/tests/__init__.py (empty)

   app/shared/tests/test_models.py:
   - Test TimestampMixin creates columns correctly
   - Test timestamps are set on model creation
   - Use a test model class that inherits the mixin
   - Verify created_at and updated_at are populated

   app/shared/tests/test_schemas.py:
   - Test PaginationParams defaults (page=1, page_size=20)
   - Test PaginationParams validation (page >= 1, page_size 1-100)
   - Test PaginationParams.offset calculation
   - Test PaginatedResponse structure with mock data
   - Test PaginatedResponse total_pages calculation
   - Test ErrorResponse structure

   app/shared/tests/test_utils.py:
   - Test utcnow() returns timezone-aware datetime
   - Test format_iso() returns ISO 8601 string

Test requirements:
- Unit tests (no database needed): pytest app/shared/tests/ -v
- Integration tests: mark with @pytest.mark.integration
- All linting (ruff, mypy, pyright) must pass

Expected test results:
- test_models.py: ~3 tests
- test_schemas.py: ~6 tests
- test_utils.py: ~2 tests
- Total: ~11 new tests

When everything is green, let the user know we are ready to commit and all validations pass

Output format:
Summary: [shared infrastructure created]
Files created: [list with descriptions]
Patterns established: [pagination, timestamps, utilities]
Test results: [test counts and coverage]
Usage examples: [how to use TimestampMixin, PaginationParams]
```
