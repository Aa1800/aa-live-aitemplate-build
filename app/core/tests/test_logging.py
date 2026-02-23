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
    assert "exception" in data
