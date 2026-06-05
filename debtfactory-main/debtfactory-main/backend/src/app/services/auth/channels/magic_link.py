"""Emailed magic-link authentication channel. Stub: signatures only."""

from __future__ import annotations

from app.services.auth.channels.base import AuthChannel
from app.services.auth.schemas import LoginRequest, UserPublic


class MagicLinkChannel(AuthChannel):
    """Emailed magic-link channel."""

    name = "magic_link"

    async def authenticate(self, request: LoginRequest) -> UserPublic:
        """Authenticate a Emailed magic-link request.  TODO(auth)."""
        raise NotImplementedError
