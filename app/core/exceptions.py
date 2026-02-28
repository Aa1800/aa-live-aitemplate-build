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


_STATUS_MAP: dict[type[Exception], int] = {
    NotFoundError: 404,
    ValidationError: 422,
    DatabaseError: 500,
}


async def database_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return a structured JSON error response for database exceptions."""
    status_code = _STATUS_MAP.get(type(exc), 500)
    logger.error(
        "database.error",
        error=str(exc),
        exc_type=type(exc).__name__,
        path=request.url.path,
        exc_info=True,
    )
    return JSONResponse(
        status_code=status_code,
        content={"error": str(exc), "type": type(exc).__name__},
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Register database exception handlers on the FastAPI application."""
    app.add_exception_handler(DatabaseError, database_exception_handler)
