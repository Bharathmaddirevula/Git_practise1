"""Shared pytest fixtures: app, HTTP client, and database session.

Service-specific fixtures live in each service's own ``conftest.py``; only
cross-cutting fixtures (the app, an ``httpx.AsyncClient`` bound to it, and an
async DB session) belong here.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest.fixture(scope="session")
def app():
    """Build the FastAPI application once per test session."""
    return create_app()


@pytest_asyncio.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    """An async HTTP client wired to the app via ASGI transport."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
