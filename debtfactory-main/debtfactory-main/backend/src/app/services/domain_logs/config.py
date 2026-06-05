"""Domain Logs settings fragment (``DOMAIN_LOGS_`` env prefix). Stub only."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class DomainLogsSettings(BaseSettings):
    """Configuration for the Domain Logs service."""

    model_config = SettingsConfigDict(env_prefix="DOMAIN_LOGS_", extra="ignore")

    # Streaming knobs.
    heartbeat_seconds: int = 15
    max_buffer_lines: int = 1000

    # TODO(domain_logs): default log source path / connection.
