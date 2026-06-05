"""Auth orchestration layer. Stub: signatures only."""

from __future__ import annotations

from app.services.auth.schemas import LoginRequest, TokenPair


class AuthService:
    """Coordinates channel authentication and token issuance."""

    def login(self, request: LoginRequest) -> TokenPair:
        """Authenticate via the selected channel and issue tokens.

        TODO(auth): resolve channel, verify, mint access + refresh tokens.
        """
        raise NotImplementedError

    def refresh(self, refresh_token: str) -> TokenPair:
        """Rotate a refresh token into a fresh token pair.

        TODO(auth): validate, rotate, revoke prior refresh token.
        """
        raise NotImplementedError

    def logout(self, refresh_token: str) -> None:
        """Revoke the session behind ``refresh_token``.

        TODO(auth): mark the session revoked.
        """
        raise NotImplementedError
