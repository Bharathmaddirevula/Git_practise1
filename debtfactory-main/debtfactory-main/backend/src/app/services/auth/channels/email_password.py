"""Email + password authentication channel. Stub: signatures only."""

from __future__ import annotations

from app.services.auth.channels.base import AuthChannel
from app.services.auth.schemas import LoginRequest, UserPublic


class EmailPasswordChannel(AuthChannel):
    """Email + password channel."""

    name = "email_password"

    async def authenticate(self, request: LoginRequest) -> UserPublic:
        """Authenticate a Email + password request.  TODO(auth)."""
        raise NotImplementedError
