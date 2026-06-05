"""Auth service exceptions."""

from __future__ import annotations

from app.core.exceptions import AppException


class InvalidCredentialsError(AppException):
    """Raised when credentials do not authenticate."""

    status_code = 401
    code = "invalid_credentials"


class ChannelNotSupportedError(AppException):
    """Raised when an unknown auth channel is requested."""

    status_code = 400
    code = "channel_not_supported"


class TokenError(AppException):
    """Raised when a token is invalid, expired, or revoked."""

    status_code = 401
    code = "token_error"
