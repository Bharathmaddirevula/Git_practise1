"""Auth service constants."""

from __future__ import annotations

from typing import Final

SERVICE_NAME: Final[str] = "auth"
ROUTE_PREFIX: Final[str] = "/auth"

# Supported authentication channel identifiers.
CHANNEL_EMAIL_PASSWORD: Final[str] = "email_password"
CHANNEL_OTP_SMS: Final[str] = "otp_sms"
CHANNEL_OAUTH_GOOGLE: Final[str] = "oauth_google"
CHANNEL_MAGIC_LINK: Final[str] = "magic_link"

# TODO(auth): token TTLs, header names, etc.
