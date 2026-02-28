from datetime import UTC, datetime

from app.shared.utils import format_iso, utcnow


def test_utcnow_returns_timezone_aware_datetime() -> None:
    result = utcnow()
    assert result.tzinfo is not None
    assert result.tzinfo == UTC


def test_format_iso_returns_iso8601_string() -> None:
    dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
    result = format_iso(dt)
    assert result == "2024-01-15T10:30:00+00:00"
