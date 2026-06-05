"""Base application settings.

Defines the root :class:`Settings` model (env-driven via ``pydantic-settings``)
covering process-wide concerns: app metadata, environment, and the database URL.
Per-service configuration lives in each service's own ``config.py`` fragment and
is composed by :mod:`app.core.settings_registry` — nothing service-specific
belongs here.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["local", "dev", "staging", "prod", "test"]


class Settings(BaseSettings):
    """Root settings shared by the whole application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "loan-platform-backend"
    version: str = "0.1.0"
    environment: Environment = "local"
    debug: bool = False

    # Async SQLAlchemy database URL (e.g. postgresql+asyncpg://...).
    database_url: str = Field(
        default="postgresql+asyncpg://loan:loan@localhost:5432/loan_platform",
    )
    # Echo SQL — handy in local development only.
    database_echo: bool = False


@lru_cache
def get_settings() -> Settings:
    """Return the cached root settings instance."""
    return Settings()
