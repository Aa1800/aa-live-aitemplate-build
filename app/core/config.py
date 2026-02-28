"""Application configuration.

Settings are loaded from environment variables and an optional .env file.
Access settings via get_settings() which returns a cached singleton.

ALLOWED_ORIGINS supports both JSON array and comma-separated string formats:
    ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8123
    ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8123"]
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class _CommaFallbackEnvSource(EnvSettingsSource):
    """EnvSettingsSource that falls back to comma-split parsing for list fields.

    pydantic-settings v2 requires JSON for complex types by default.
    This subclass tries JSON first, then falls back to comma-separated parsing
    so that env vars like ``ALLOWED_ORIGINS=a.com,b.com`` work correctly.
    """

    def decode_complex_value(
        self,
        field_name: str,
        field: FieldInfo,
        value: Any,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        try:
            return super().decode_complex_value(field_name, field, value)
        except Exception:
            if isinstance(value, str):
                return [item.strip() for item in value.split(",") if item.strip()]
            raise


class Settings(BaseSettings):
    """Application-wide configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Obsidian Agent Project"
    version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api"

    # CORS — allowed origins for cross-origin requests
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8123",
    ]

    # Database
    database_url: str

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            _CommaFallbackEnvSource(settings_cls),
            dotenv_settings,
            file_secret_settings,
        )


@lru_cache
def get_settings() -> Settings:
    """Return the cached Settings singleton."""
    return Settings()  # type: ignore[call-arg]
