# Structured Logging Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `structlog` with JSON output, request-ID correlation, and the hybrid dotted-namespace event convention to `app/core/logging.py`.

**Architecture:** A single `setup_logging()` call configures structlog globally with a processor chain that injects request IDs from `contextvars`, formats timestamps as ISO-8601, renders exceptions as JSON, and emits newline-delimited JSON to stdout. All callers use `get_logger()` which returns a typed `BoundLogger`.

**Tech Stack:** Python 3.12, `structlog`, `contextvars`, `uv`, `ruff`, `mypy`, `pyright`, `pytest`

---

### Task 1: Install structlog and scaffold the package

**Files:**
- Create: `app/__init__.py`
- Create: `app/core/__init__.py`
- Create: `app/core/tests/__init__.py`

**Step 1: Install structlog**

```bash
uv add structlog
```

Expected: `structlog` appears in `pyproject.toml` under `dependencies`.

**Step 2: Create package markers**

```bash
mkdir -p app/core/tests
touch app/__init__.py app/core/__init__.py app/core/tests/__init__.py
```

**Step 3: Verify import works**

```bash
uv run python -c "import structlog; print(structlog.__version__)"
```

Expected: version string printed, no errors.

**Step 4: Commit**

```bash
git add app/ pyproject.toml uv.lock
git commit -m "feat: install structlog and scaffold app/ package"
```

---

### Task 2: Update pyproject.toml for the new app/ layout

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add ruff per-file-ignores for app tests**

In `[tool.ruff.lint.per-file-ignores]`, add:

```toml
"app/**/tests/**/*.py" = ["S101", "ANN"]
```

**Step 2: Add mypy override for app test modules**

Append after the existing `[[tool.mypy.overrides]]` block:

```toml
[[tool.mypy.overrides]]
module = "app.core.tests.*"
disallow_untyped_defs = false
disallow_incomplete_defs = false
```

**Step 3: Update pytest testpaths**

Change:
```toml
testpaths = ["tests"]
```
To:
```toml
testpaths = ["tests", "app"]
```

**Step 4: Verify existing tests still pass**

```bash
uv run pytest -v
```

Expected: 24 tests pass (no regressions).

**Step 5: Commit**

```bash
git add pyproject.toml
git commit -m "chore: extend ruff/mypy/pytest config for app/ package"
```

---

### Task 3: Write failing tests for logging module

**Files:**
- Create: `app/core/tests/test_logging.py`

**Step 1: Write the tests**

```python
"""Tests for app/core/logging.py."""

from __future__ import annotations

import io
import json
import logging

import structlog

from app.core.logging import get_logger, get_request_id, set_request_id, setup_logging


def test_setup_logging_does_not_raise() -> None:
    setup_logging()


def test_setup_logging_custom_level() -> None:
    setup_logging(log_level="DEBUG")
    root = logging.getLogger()
    assert root.level == logging.DEBUG


def test_set_request_id_generates_uuid_when_no_arg() -> None:
    rid = set_request_id()
    assert len(rid) == 36  # UUID4 canonical form: 8-4-4-4-12
    assert rid.count("-") == 4


def test_set_request_id_stores_supplied_value() -> None:
    set_request_id("my-trace-id")
    assert get_request_id() == "my-trace-id"


def test_get_request_id_returns_set_value() -> None:
    set_request_id("abc-123")
    assert get_request_id() == "abc-123"


def test_get_logger_returns_bound_logger() -> None:
    setup_logging()
    logger = get_logger("test")
    assert isinstance(logger, structlog.stdlib.BoundLogger)


def test_request_id_appears_in_log_output(capsys: pytest.CaptureFixture[str]) -> None:
    import pytest  # local import to satisfy ANN ignore scope

    setup_logging(log_level="INFO")
    set_request_id("req-xyz")
    logger = get_logger("test.output")
    logger.info("ping.sent")
    captured = capsys.readouterr()
    # Each line is a JSON object
    data = json.loads(captured.out.strip())
    assert data["request_id"] == "req-xyz"
    assert data["event"] == "ping.sent"


def test_exc_info_renders_exception(capsys: pytest.CaptureFixture[str]) -> None:
    import pytest  # local import to satisfy ANN ignore scope

    setup_logging(log_level="ERROR")
    logger = get_logger("test.exc")
    try:
        raise ValueError("boom")
    except ValueError:
        logger.exception("task.processing_failed")
    captured = capsys.readouterr()
    data = json.loads(captured.out.strip())
    assert data["event"] == "task.processing_failed"
    assert "exception" in data or "exc_info" in data or "traceback" in data
```

Wait — the import of `pytest` at the top of the file is cleaner. Let me write the correct version:

```python
"""Tests for app/core/logging.py."""

from __future__ import annotations

import json
import logging

import pytest
import structlog

from app.core.logging import get_logger, get_request_id, set_request_id, setup_logging


def test_setup_logging_does_not_raise() -> None:
    setup_logging()


def test_setup_logging_custom_level() -> None:
    setup_logging(log_level="DEBUG")
    root = logging.getLogger()
    assert root.level == logging.DEBUG


def test_set_request_id_generates_uuid_when_no_arg() -> None:
    rid = set_request_id()
    assert len(rid) == 36
    assert rid.count("-") == 4


def test_set_request_id_stores_supplied_value() -> None:
    set_request_id("my-trace-id")
    assert get_request_id() == "my-trace-id"


def test_get_request_id_returns_set_value() -> None:
    set_request_id("abc-123")
    assert get_request_id() == "abc-123"


def test_get_logger_returns_bound_logger() -> None:
    setup_logging()
    logger = get_logger("test")
    assert isinstance(logger, structlog.stdlib.BoundLogger)


def test_request_id_in_log_output(capsys: pytest.CaptureFixture[str]) -> None:
    setup_logging(log_level="INFO")
    set_request_id("req-xyz")
    logger = get_logger("test.output")
    logger.info("ping.sent")
    captured = capsys.readouterr()
    data = json.loads(captured.out.strip())
    assert data["request_id"] == "req-xyz"
    assert data["event"] == "ping.sent"


def test_exc_info_renders_exception(capsys: pytest.CaptureFixture[str]) -> None:
    setup_logging(log_level="ERROR")
    logger = get_logger("test.exc")
    try:
        raise ValueError("boom")
    except ValueError:
        logger.exception("task.processing_failed")
    captured = capsys.readouterr()
    data = json.loads(captured.out.strip())
    assert data["event"] == "task.processing_failed"
    # structlog ExceptionRenderer puts traceback under "exception" key
    assert "exception" in data
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest app/core/tests/test_logging.py -v
```

Expected: `ModuleNotFoundError: No module named 'app.core.logging'`

**Step 3: Commit the failing tests**

```bash
git add app/core/tests/test_logging.py
git commit -m "test: add failing tests for structured logging module"
```

---

### Task 4: Implement app/core/logging.py

**Files:**
- Create: `app/core/logging.py`

**Step 1: Write the implementation**

```python
"""Structured logging configuration for the application.

Uses structlog with JSON output, ISO timestamps, and request-ID correlation
via a contextvars.ContextVar so the ID is propagated across async calls
without any explicit passing.

Event naming convention (hybrid dotted namespace):
    {domain}.{component}.{action}_{state}

Examples:
    user.registration_started
    database.connection_initialized
    request.processing_failed

States: _started, _completed, _failed, _validated, _rejected
"""

from __future__ import annotations

import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any

import structlog
from structlog.types import EventDict, WrappedLogger

# ---------------------------------------------------------------------------
# Request-ID correlation
# ---------------------------------------------------------------------------

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def set_request_id(request_id: str | None = None) -> str:
    """Set (or generate) the request ID for the current async context.

    Args:
        request_id: Explicit ID to use. A UUID4 is generated when omitted.

    Returns:
        The ID that was stored.
    """
    rid = request_id if request_id is not None else str(uuid.uuid4())
    request_id_var.set(rid)
    return rid


def get_request_id() -> str:
    """Return the request ID stored in the current async context."""
    return request_id_var.get()


# ---------------------------------------------------------------------------
# Structlog processors
# ---------------------------------------------------------------------------


def _add_request_id(
    logger: WrappedLogger,  # noqa: ARG001
    method: str,  # noqa: ARG001
    event_dict: EventDict,
) -> EventDict:
    """Structlog processor: inject request_id into every log event."""
    rid = request_id_var.get()
    if rid:
        event_dict["request_id"] = rid
    return event_dict


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------


def setup_logging(log_level: str = "INFO") -> None:
    """Configure structlog for JSON output.

    Call once at application startup. Subsequent calls reconfigure the
    root logger level and reset structlog's processor chain.

    Args:
        log_level: Standard Python log level name (DEBUG, INFO, WARNING, …).
    """
    numeric_level: int = getattr(logging, log_level.upper(), logging.INFO)

    processors: list[Any] = [
        _add_request_id,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.ExceptionRenderer(),
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=False,
    )

    # Also configure stdlib root logger so that libraries using logging
    # are captured at the right level.
    root = logging.getLogger()
    root.setLevel(numeric_level)
    if not root.handlers:
        root.addHandler(logging.StreamHandler(sys.stdout))


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a structlog BoundLogger.

    Args:
        name: Optional logger name (appears as the ``logger`` key in JSON).

    Returns:
        A configured BoundLogger instance.
    """
    logger: structlog.stdlib.BoundLogger = structlog.get_logger(name)
    return logger
```

Note on `list[Any]` for processors: structlog's `Processor` type alias is
`Callable[[WrappedLogger, str, EventDict], EventDict]`, but the built-in
processors are typed as such while `JSONRenderer` has a slightly different
signature. Using `list[Any]` avoids a pyright false positive here without
silencing real errors.

**Step 2: Run tests**

```bash
uv run pytest app/core/tests/test_logging.py -v
```

Expected: all 8 tests pass.

**Step 3: Run linters and type checkers**

```bash
uv run ruff check app/
uv run mypy app/
uv run pyright app/
```

Fix any issues before continuing.

**Step 4: Commit**

```bash
git add app/core/logging.py
git commit -m "feat: add structured logging module with JSON output and request-ID correlation"
```

---

### Task 5: Create app/main.py usage demo

**Files:**
- Create: `app/main.py`

**Step 1: Write the demo**

```python
"""Demo: structured logging usage patterns.

Run with: uv run python -m app.main
"""

from __future__ import annotations

from app.core.logging import get_logger, set_request_id, setup_logging


def simulate_registration(email: str) -> None:
    """Show the hybrid dotted namespace pattern for a user flow."""
    logger = get_logger("app.users")

    logger.info("user.registration_started", email=email, source="api")

    # Simulate validation
    if "@" not in email:
        logger.warning("user.registration_rejected", email=email, reason="invalid_email")
        return

    user_id = "usr_abc123"
    logger.info("user.registration_completed", user_id=user_id, email=email)


def simulate_db_init() -> None:
    """Show infrastructure-level logging."""
    logger = get_logger("app.database")
    logger.info("database.connection_initialized", host="localhost", port=5432)


def simulate_failure() -> None:
    """Show exception logging with stack trace."""
    logger = get_logger("app.tasks")
    try:
        raise RuntimeError("upstream timeout")
    except RuntimeError:
        logger.exception("task.processing_failed", task="send_email")


def main() -> None:
    setup_logging(log_level="INFO")
    set_request_id("demo-request-001")

    simulate_db_init()
    simulate_registration("alice@example.com")
    simulate_registration("not-an-email")
    simulate_failure()


if __name__ == "__main__":
    main()
```

**Step 2: Run the demo**

```bash
uv run python -m app.main
```

Expected: newline-delimited JSON log lines, each containing `request_id`, `level`, `timestamp`, and `event` following the dotted namespace pattern. The last line should contain `"exception"` with a stack trace.

**Step 3: Run full checks**

```bash
uv run ruff check .
uv run mypy app/
uv run pyright app/
uv run pytest -v
```

All must be green.

**Step 4: Commit**

```bash
git add app/main.py
git commit -m "feat: add app/main.py logging usage demo"
```

---

### Task 6: Final validation and commit

**Step 1: Run the full test suite**

```bash
uv run pytest -v
```

Expected: 24 existing tests + 8 new logging tests = 32 tests passing.

**Step 2: Run all linters and type checkers**

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy app/ main.py
uv run pyright
```

Expected: zero errors.

**Step 3: Commit the design doc**

```bash
git add docs/
git commit -m "docs: add structured logging design doc"
```

**Step 4: Run /commit** (or let Claude do it)

---

## Troubleshooting

**`structlog.configure` processor type errors under pyright strict**

If pyright complains about the `processors` list, annotate it as `list[Any]` (already done above). This is a known limitation of structlog's type stubs where `JSONRenderer`'s return type (`bytes | str`) differs from the `EventDict` the chain expects.

**`cache_logger_on_first_use=True` makes tests flaky**

Set to `False` in `setup_logging()`. Caching means the first test configures structlog and later tests see stale processors. Keeping it `False` ensures each `setup_logging()` call takes effect.

**`capsys` captures nothing**

`PrintLoggerFactory(file=sys.stdout)` writes to `sys.stdout`. pytest's `capsys` intercepts `sys.stdout`. This combination works. If you switch to `StreamHandler`-based stdlib integration, use `caplog` instead.
