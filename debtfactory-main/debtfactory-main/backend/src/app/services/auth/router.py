"""Auth HTTP router. Module-level ``router`` is auto-discovered."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from app.services.auth.constants import ROUTE_PREFIX
from app.services.auth.dependencies import get_auth_service
from app.services.auth.schemas import LoginRequest, TokenPair
from app.services.auth.service import AuthService

router = APIRouter(prefix=ROUTE_PREFIX, tags=["auth"])


@router.post("/login", response_model=TokenPair, status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    """Authenticate via the selected channel.  TODO(auth)."""
    raise NotImplementedError


@router.post("/refresh", response_model=TokenPair, status_code=status.HTTP_200_OK)
async def refresh(
    refresh_token: str,
    service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    """Rotate a refresh token.  TODO(auth)."""
    raise NotImplementedError


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_token: str,
    service: AuthService = Depends(get_auth_service),
) -> Response:
    """Revoke the current session.  TODO(auth)."""
    raise NotImplementedError
