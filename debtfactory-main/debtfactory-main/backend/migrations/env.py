"""Async, multi-branch-aware Alembic environment.

Each service owns a branch label and a version subdirectory
(``migrations/versions/<service>/``) so teams generate revisions on their own
labelled head without colliding on a single linear history.

Model metadata is collected from the shared declarative :class:`Base`; importing
every service's ``models`` module registers its tables for autogenerate.
"""

from __future__ import annotations

import asyncio
import importlib
import pkgutil
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

import app.services as services_pkg
from app.core.config import get_settings
from app.core.database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Inject the runtime database URL from settings.
config.set_main_option("sqlalchemy.url", get_settings().database_url)


def _import_all_models() -> None:
    """Import every ``services/<name>/models.py`` so tables register on Base."""
    for module_info in pkgutil.iter_modules(services_pkg.__path__):
        if not module_info.ispkg:
            continue
        try:
            importlib.import_module(f"{services_pkg.__name__}.{module_info.name}.models")
        except ModuleNotFoundError:
            continue


_import_all_models()
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (emits SQL)."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def _do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations against a live async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        future=True,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(_do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
