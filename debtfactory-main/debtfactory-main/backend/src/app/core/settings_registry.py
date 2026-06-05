"""Per-service settings composition.

Each service ships a ``config.py`` exposing a ``Settings`` subclass with a unique
env prefix (``RULE_ENGINE_``, ``AUTH_``, ...). This registry discovers those
fragments by walking ``app/services/*/config.py`` and instantiates each one, so
the root app never maintains a global list of settings classes.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import Any

from pydantic_settings import BaseSettings

import app.services as services_pkg
from app.core.logging import get_logger

logger = get_logger(__name__)


def discover_service_settings() -> dict[str, BaseSettings]:
    """Instantiate every service ``Settings`` fragment, keyed by service name.

    A fragment is any subclass of :class:`pydantic_settings.BaseSettings`
    exported from ``services/<name>/config.py``. Services without one are
    skipped silently.
    """
    fragments: dict[str, BaseSettings] = {}
    for module_info in pkgutil.iter_modules(services_pkg.__path__):
        if not module_info.ispkg:
            continue
        module_name = f"{services_pkg.__name__}.{module_info.name}.config"
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
        settings_cls = _find_settings_class(module)
        if settings_cls is not None:
            fragments[module_info.name] = settings_cls()
            logger.info("composed settings fragment for '%s'", module_info.name)
    return fragments


def _find_settings_class(module: Any) -> type[BaseSettings] | None:
    """Return the first ``BaseSettings`` subclass defined in ``module``."""
    for value in vars(module).values():
        if (
            isinstance(value, type)
            and issubclass(value, BaseSettings)
            and value is not BaseSettings
            and value.__module__ == module.__name__
        ):
            return value
    return None
