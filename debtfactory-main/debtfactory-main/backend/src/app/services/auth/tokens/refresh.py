"""Opaque refresh-token issue/verify/rotate helpers. Stub only."""

from __future__ import annotations


def issue_refresh_token(user_id: int) -> str:
    """Create a new opaque refresh token for ``user_id``.  TODO(auth)."""
    raise NotImplementedError


def verify_refresh_token(token: str) -> int:
    """Validate a refresh token and return its user id.  TODO(auth)."""
    raise NotImplementedError
