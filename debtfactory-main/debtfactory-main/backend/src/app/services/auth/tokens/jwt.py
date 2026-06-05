"""JWT access-token encode/decode helpers. Stub: signatures only."""

from __future__ import annotations

from typing import Any


def encode_access_token(claims: dict[str, Any]) -> str:
    """Sign ``claims`` into a JWT access token.  TODO(auth)."""
    raise NotImplementedError


def decode_access_token(token: str) -> dict[str, Any]:
    """Verify and decode a JWT access token.  TODO(auth)."""
    raise NotImplementedError
