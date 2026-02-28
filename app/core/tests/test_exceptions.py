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

    assert isinstance(response.body, bytes)
    body = json.loads(response.body.decode())
    assert body["error"] == "connection timeout"
    assert body["type"] == "DatabaseError"
    assert response.status_code == 500


async def test_not_found_error_returns_404() -> None:
    request = MagicMock(spec=Request)
    request.url.path = "/test"
    exc = NotFoundError("user not found")

    with patch("app.core.exceptions.logger"):
        response = await database_exception_handler(request, exc)

    assert response.status_code == 404


async def test_exception_handler_logs_with_exc_info() -> None:
    request = MagicMock(spec=Request)
    request.url.path = "/test"
    exc = NotFoundError("record missing")

    with patch("app.core.exceptions.logger") as mock_logger:
        await database_exception_handler(request, exc)

    mock_logger.error.assert_called_once()
    call_kwargs = mock_logger.error.call_args.kwargs
    assert call_kwargs.get("exc_info") is True
