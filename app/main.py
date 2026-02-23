"""Demo: structured logging usage patterns.

Demonstrates the hybrid dotted namespace event convention:
    {domain}.{component}.{action}_{state}

Run with: uv run python -m app.main
"""

from __future__ import annotations

from app.core.logging import get_logger, set_request_id, setup_logging


def simulate_registration(email: str) -> None:
    """Show the hybrid dotted namespace pattern for a user registration flow."""
    logger = get_logger("app.users")

    logger.info("user.registration_started", email=email, source="api")

    if "@" not in email:
        logger.warning(
            "user.registration_rejected", email=email, reason="invalid_email"
        )
        return

    user_id = "usr_abc123"
    logger.info("user.registration_completed", user_id=user_id, email=email)


def simulate_db_init() -> None:
    """Show infrastructure-level logging."""
    logger = get_logger("app.database")
    logger.info("database.connection_initialized", host="localhost", port=5432)


def simulate_failure() -> None:
    """Show exception logging with a full stack trace in JSON output."""
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
