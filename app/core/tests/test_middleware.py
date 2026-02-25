"""Tests for app/core/middleware.py."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.logging import request_id_var
from app.core.middleware import RequestLoggingMiddleware, setup_middleware


@pytest.fixture(autouse=True)
def reset_request_id() -> Generator[None, None, None]:
    """Reset request_id ContextVar between tests."""
    token = request_id_var.set("")
    yield
    request_id_var.reset(token)


@pytest.fixture
def simple_app() -> FastAPI:
    """FastAPI app with RequestLoggingMiddleware and a basic GET endpoint."""
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/ping")
    async def ping() -> dict[str, str]:
        return {"pong": "ok"}

    return app


async def test_middleware_adds_request_id_to_response(
    simple_app: FastAPI,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=simple_app), base_url="http://test"
    ) as client:
        response = await client.get("/ping")
    assert "x-request-id" in response.headers
    assert len(response.headers["x-request-id"]) == 36  # UUID4 format


async def test_middleware_uses_provided_request_id(simple_app: FastAPI) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=simple_app), base_url="http://test"
    ) as client:
        response = await client.get("/ping", headers={"X-Request-ID": "test-abc-123"})
    assert response.headers["x-request-id"] == "test-abc-123"


async def test_middleware_logs_request_started(simple_app: FastAPI) -> None:
    with patch("app.core.middleware.logger") as mock_logger:
        mock_logger.info = MagicMock()
        async with AsyncClient(
            transport=ASGITransport(app=simple_app), base_url="http://test"
        ) as client:
            await client.get("/ping")
    events = [call.args[0] for call in mock_logger.info.call_args_list]
    assert "request.started" in events


async def test_middleware_logs_request_completed(simple_app: FastAPI) -> None:
    with patch("app.core.middleware.logger") as mock_logger:
        mock_logger.info = MagicMock()
        async with AsyncClient(
            transport=ASGITransport(app=simple_app), base_url="http://test"
        ) as client:
            await client.get("/ping")
    events = [call.args[0] for call in mock_logger.info.call_args_list]
    assert "request.completed" in events


async def test_setup_middleware_adds_cors() -> None:
    app = FastAPI()
    setup_middleware(app)

    @app.get("/ping")
    async def ping() -> dict[str, str]:
        return {"pong": "ok"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.options(
            "/ping",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
    assert (
        response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    )
