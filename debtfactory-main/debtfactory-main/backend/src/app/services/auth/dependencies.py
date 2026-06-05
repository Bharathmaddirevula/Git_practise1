"""Auth FastAPI dependencies: current user, channel resolver. Stub only."""

from __future__ import annotations

from app.services.auth.channels.base import AuthChannel
from app.services.auth.schemas import UserPublic
from app.services.auth.service import AuthService


def get_auth_service() -> AuthService:
    """Provide an :class:`AuthService`.

    TODO(auth): construct with repositories + token services.
    """
    raise NotImplementedError


def resolve_channel(channel: str) -> AuthChannel:
    """Return the :class:`AuthChannel` implementation for ``channel``.

    TODO(auth): look up the registered channel; raise
    ChannelNotSupportedError if unknown.
    """
    raise NotImplementedError


async def current_user() -> UserPublic:
    """Resolve the authenticated user from the bearer token.

    TODO(auth): decode/verify the access token and load the user.
    """
    raise NotImplementedError
