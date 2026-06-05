"""SMS one-time-password authentication channel. Stub: signatures only."""

from __future__ import annotations

from app.services.auth.channels.base import AuthChannel
from app.services.auth.schemas import LoginRequest, UserPublic


class OtpSmsChannel(AuthChannel):
    """SMS one-time-password channel."""

    name = "otp_sms"

    async def authenticate(self, request: LoginRequest) -> UserPublic:
        """Authenticate a SMS one-time-password request.  TODO(auth)."""
        raise NotImplementedError
