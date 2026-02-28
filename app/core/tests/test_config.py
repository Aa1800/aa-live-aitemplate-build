"""Tests for app/core/config.py."""

from __future__ import annotations

import pytest

from app.core.config import Settings, get_settings


def test_settings_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    # Provide the required field and bypass the .env file so field defaults are visible.
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/testdb"
    )
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.app_name == "Obsidian Agent Project"
    assert settings.version == "0.1.0"
    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.api_prefix == "/api"


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_NAME", "Test App")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/testdb"
    )
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.app_name == "Test App"
    assert settings.environment == "production"


def test_get_settings_returns_settings_instance() -> None:
    s = get_settings()
    assert isinstance(s, Settings)


def test_get_settings_is_cached() -> None:
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_allowed_origins_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/testdb"
    )
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert "http://localhost:3000" in settings.allowed_origins
    assert "http://localhost:8123" in settings.allowed_origins


def test_allowed_origins_parsed_from_comma_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://example.com,http://other.com")
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/testdb"
    )
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.allowed_origins == ["http://example.com", "http://other.com"]


def test_database_url_is_read_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/testdb"
    )
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.database_url == "postgresql+asyncpg://user:pass@localhost/testdb"
    get_settings.cache_clear()
