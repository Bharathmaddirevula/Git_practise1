"""Auth request/response DTOs (Pydantic v2). Stub: shapes only."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr


class LoginRequest(BaseModel):
    """Generic login request; ``channel`` selects the strategy."""

    model_config = ConfigDict(extra="forbid")

    channel: str
    identifier: str
    secret: str | None = None  # password / otp / token, channel-dependent


class TokenPair(BaseModel):
    """Issued access + refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    """Public-safe user representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr | None = None
