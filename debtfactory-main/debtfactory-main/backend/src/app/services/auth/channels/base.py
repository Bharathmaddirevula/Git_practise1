"""Authentication channel protocol. Stub: interface only."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.services.auth.schemas import LoginRequest, UserPublic


@runtime_checkable
class AuthChannel(Protocol):
    """A pluggable authentication strategy (email/otp/oauth/magic-link)."""

    name: str

    async def authenticate(self, request: LoginRequest) -> UserPublic:
        """Verify the request and return the authenticated user.

        TODO(auth): implement per channel.
        """
        ...
