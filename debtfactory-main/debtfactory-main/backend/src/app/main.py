"""FastAPI application factory.

Builds the ASGI app, installs middleware and exception handlers, mounts the
health endpoints, and auto-discovers every feature service router. No service is
registered by hand here — :func:`app.api.router_registry.discover_routers` walks
``app/services/*/router.py`` so adding a service touches zero shared files.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.router_registry import discover_routers
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import register_middleware


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: configure logging on startup."""
    configure_logging()
    yield


def create_app() -> FastAPI:
    """Construct and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    register_middleware(app)
    register_exception_handlers(app)

    # Health/readiness endpoints (always mounted).
    app.include_router(health_router)

    # Auto-discover and mount every feature service router.
    for router in discover_routers():
        app.include_router(router)

    return app


app = create_app()
