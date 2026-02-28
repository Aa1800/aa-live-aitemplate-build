from datetime import UTC, datetime


def utcnow() -> datetime:
    return datetime.now(UTC)


def format_iso(dt: datetime) -> str:
    return dt.isoformat()
