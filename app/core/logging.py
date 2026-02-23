"""Structured logging configuration.

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
from structlog.typing import EventDict, WrappedLogger

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def set_request_id(request_id: str | None = None) -> str:
    """Store request_id in ContextVar; generate UUID4 if not supplied."""
    rid = request_id if request_id is not None else str(uuid.uuid4())
    request_id_var.set(rid)
    return rid


def get_request_id() -> str:
    """Return the current request_id from ContextVar."""
    return request_id_var.get()


def _add_request_id(
    logger: WrappedLogger,
    method: str,
    event_dict: EventDict,
) -> EventDict:
    """Inject request_id into the event dict when present."""
    rid = request_id_var.get()
    if rid:
        event_dict["request_id"] = rid
    return event_dict


def setup_logging(log_level: str = "INFO") -> None:
    """Configure structlog globally with JSON output to stdout."""
    numeric_level: int = int(getattr(logging, log_level.upper(), logging.INFO))

    processors: list[Any] = [
        _add_request_id,
        structlog.stdlib.add_log_level,
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

    root = logging.getLogger()
    root.setLevel(numeric_level)
    if not root.handlers:
        root.addHandler(logging.StreamHandler(sys.stdout))


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a typed structlog stdlib BoundLogger."""
    proxy = (
        structlog.stdlib.get_logger(name)
        if name is not None
        else structlog.stdlib.get_logger()
    )
    return proxy.bind()
