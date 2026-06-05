"""Google OAuth 2.0 authentication channel. Stub: signatures only."""

from __future__ import annotations

from app.services.auth.channels.base import AuthChannel
from app.services.auth.schemas import LoginRequest, UserPublic


class OauthGoogleChannel(AuthChannel):
    """Google OAuth 2.0 channel."""

    name = "oauth_google"

    async def authenticate(self, request: LoginRequest) -> UserPublic:
        """Authenticate a Google OAuth 2.0 request.  TODO(auth)."""
        raise NotImplementedError
