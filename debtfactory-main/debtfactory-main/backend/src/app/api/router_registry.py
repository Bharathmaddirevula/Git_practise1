"""Router auto-discovery.

Walks ``app/services/*/router.py`` and collects every module-level ``router``
object (an :class:`fastapi.APIRouter`). This is the anti-merge-conflict core of
the architecture: services are mounted by convention, so adding one never
requires editing a shared "include every router here" list.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import TYPE_CHECKING

import app.services as services_pkg
from app.core.logging import get_logger

if TYPE_CHECKING:
    from fastapi import APIRouter

logger = get_logger(__name__)


def discover_routers() -> list[APIRouter]:
    """Import each ``services/<name>/router.py`` and return its ``router``.

    A service is included automatically as long as its ``router.py`` exposes a
    module-level object named ``router``. Services without one are skipped.
    """
    from fastapi import APIRouter

    routers: list[APIRouter] = []
    for module_info in pkgutil.iter_modules(services_pkg.__path__):
        if not module_info.ispkg:
            continue
        module_name = f"{services_pkg.__name__}.{module_info.name}.router"
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            logger.debug("service %s exposes no router module", module_info.name)
            continue
        router = getattr(module, "router", None)
        if isinstance(router, APIRouter):
            logger.info("mounted router for service '%s'", module_info.name)
            routers.append(router)
        else:
            logger.warning("service '%s' router.py has no APIRouter", module_info.name)
    return routers
