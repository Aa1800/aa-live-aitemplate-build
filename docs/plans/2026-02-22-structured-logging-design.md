# Structured Logging Design

Date: 2026-02-22

## Goal

Add `structlog` with JSON output, request ID correlation via `contextvars`, and the hybrid dotted namespace event pattern (`domain.component.action_state`) to the project.

## Files

| File | Action |
|------|--------|
| `app/__init__.py` | Create (package marker) |
| `app/core/__init__.py` | Create (package marker) |
| `app/core/logging.py` | Create (logging module) |
| `app/core/tests/__init__.py` | Create (package marker) |
| `app/core/tests/test_logging.py` | Create (unit tests) |
| `app/main.py` | Create (usage demo) |
| `pyproject.toml` | Update (ruff, mypy, pytest) |

## `app/core/logging.py` API

- `request_id_var: ContextVar[str]` — module-level, default `""`
- `set_request_id(request_id: str | None = None) -> str` — sets UUID if none given
- `get_request_id() -> str` — reads context var
- `setup_logging(log_level: str = "INFO") -> None` — configures structlog globally
- `get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger` — typed wrapper

### structlog processors (in order)

1. `_add_request_id` — injects `request_id` from context var
2. `structlog.stdlib.add_log_level` — adds `level` field
3. `structlog.stdlib.add_logger_name` — adds `logger` field
4. `structlog.processors.TimeStamper(fmt="iso")` — ISO timestamp
5. `structlog.processors.StackInfoRenderer()` — stack_info support
6. `structlog.processors.ExceptionRenderer()` — exc_info → JSON stack traces
7. `structlog.processors.JSONRenderer()` — final JSON output

## Event naming convention

```
{domain}.{component}.{action}_{state}
```

States: `_started`, `_completed`, `_failed`, `_validated`, `_rejected`

Examples:
- `user.registration_started`
- `database.connection_initialized`
- `request.processing_failed`

## `pyproject.toml` changes

```toml
# ruff per-file-ignores: add
"app/**/tests/**/*.py" = ["S101", "ANN"]

# mypy overrides: add
[[tool.mypy.overrides]]
module = "app.core.tests.*"
disallow_untyped_defs = false
disallow_incomplete_defs = false

# pytest testpaths: update
testpaths = ["tests", "app"]
```

## Tests

- `setup_logging()` runs without error
- `set_request_id()` without arg → UUID string returned and stored
- `set_request_id("custom-id")` → exact value stored and retrievable
- `get_request_id()` returns stored value
- Request ID injected into log event dict via processor
- `exc_info=True` produces stack trace in rendered output
