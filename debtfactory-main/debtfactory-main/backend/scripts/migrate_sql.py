"""Apply plain-SQL migrations from ``migrations/sql/`` to PostgreSQL.

Recommended SQL-file migration pattern (no Alembic for these services): each
``*.up.sql`` file is applied once, in sorted path order, inside a transaction,
and recorded in a ``schema_migrations`` tracking table so re-runs are a no-op.

Usage:
    python scripts/migrate_sql.py            # apply all pending *.up.sql
    python scripts/migrate_sql.py --status   # show applied vs pending
    python scripts/migrate_sql.py --down NAME # run a single *.down.sql, e.g. auth/0001_init

The database URL comes from app settings (``DATABASE_URL`` / ``.env``); the
``+asyncpg`` SQLAlchemy driver suffix is stripped for the raw asyncpg DSN.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

import asyncpg

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from app.core.config import get_settings  # noqa: E402

SQL_DIR = Path(__file__).resolve().parent.parent / "migrations" / "sql"
_TRACKING_DDL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    filename    TEXT PRIMARY KEY,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


def _dsn() -> str:
    """Raw asyncpg DSN (drop the SQLAlchemy ``+asyncpg`` driver suffix)."""
    return get_settings().database_url.replace("+asyncpg", "")


def _up_files() -> list[Path]:
    return sorted(SQL_DIR.glob("**/*.up.sql"))


def _key(path: Path) -> str:
    return path.relative_to(SQL_DIR).as_posix()


async def _apply(args: argparse.Namespace) -> int:
    conn = await asyncpg.connect(_dsn())
    try:
        await conn.execute(_TRACKING_DDL)
        rows = await conn.fetch("SELECT filename FROM schema_migrations")
        applied = {r["filename"] for r in rows}

        if args.status:
            for f in _up_files():
                mark = "applied" if _key(f) in applied else "PENDING"
                print(f"  [{mark}] {_key(f)}")
            return 0

        if args.down:
            path = SQL_DIR / f"{args.down}.down.sql"
            if not path.exists():
                print(f"down file not found: {path}")
                return 1
            up_key = f"{args.down}.up.sql"
            async with conn.transaction():
                await conn.execute(path.read_text(encoding="utf-8"))
                await conn.execute("DELETE FROM schema_migrations WHERE filename = $1", up_key)
            print(f"rolled back {args.down}")
            return 0

        pending = [f for f in _up_files() if _key(f) not in applied]
        if not pending:
            print("nothing to apply (up to date)")
            return 0
        for f in pending:
            async with conn.transaction():
                await conn.execute(f.read_text(encoding="utf-8"))
                await conn.execute("INSERT INTO schema_migrations (filename) VALUES ($1)", _key(f))
            print(f"applied {_key(f)}")
        return 0
    finally:
        await conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply plain-SQL migrations.")
    parser.add_argument("--status", action="store_true", help="show applied vs pending")
    parser.add_argument(
        "--down", metavar="NAME", help="roll back one migration, e.g. auth/0001_init"
    )
    return asyncio.run(_apply(parser.parse_args()))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
