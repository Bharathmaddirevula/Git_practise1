"""Auth settings fragment (``AUTH_`` env prefix).

Composed by :mod:`app.core.settings_registry`. Stub only.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    """Configuration for the Auth service."""

    model_config = SettingsConfigDict(env_prefix="AUTH_", extra="ignore")

    # Signing + lifetimes. Provide real secrets via env / secret manager.
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_ttl_seconds: int = 900
    refresh_token_ttl_seconds: int = 1209600

    # TODO(auth): OAuth client ids/secrets, SMS/email provider keys.
