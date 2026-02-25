"""Request logging middleware.

Integrates with app.core.logging for structured JSON logging with
request-ID correlation. Every request gets a unique ID that propagates
through all log lines emitted during that request.
"""

from __future__ import annotations

import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import get_settings
from app.core.logging import get_logger, get_request_id, set_request_id

logger = get_logger("app.core.middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with a correlation ID and wall-clock timing."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID")
        set_request_id(request_id)

        start_time = time.perf_counter()
        logger.info(
            "request.started",
            method=request.method,
            path=request.url.path,
            client_host=request.client.host if request.client else None,
        )

        try:
            response = await call_next(request)
            duration = time.perf_counter() - start_time
            logger.info(
                "request.completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_seconds=round(duration, 3),
            )
            response.headers["X-Request-ID"] = get_request_id()
            return response

        except Exception:
            duration = time.perf_counter() - start_time
            logger.error(
                "request.failed",
                method=request.method,
                path=request.url.path,
                duration_seconds=round(duration, 3),
                exc_info=True,
            )
            raise


def setup_middleware(app: FastAPI) -> None:
    """Add request logging and CORS middleware to the application."""
    settings = get_settings()
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
