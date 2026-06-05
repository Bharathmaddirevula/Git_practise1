"""Liveness and readiness endpoints.

``/health`` is a cheap liveness probe (the process is up). ``/readyz`` performs
a lightweight dependency check (database connectivity) so orchestrators only
route traffic once the app can serve it.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe: returns 200 as long as the process is serving."""
    return {"status": "ok"}


@router.get("/readyz")
async def readyz(session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    """Readiness probe: confirms the database is reachable."""
    await session.execute(text("SELECT 1"))
    return {"status": "ready"}
