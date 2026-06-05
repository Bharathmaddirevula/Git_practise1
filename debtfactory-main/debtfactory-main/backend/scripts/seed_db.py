"""CLI: seed the database with baseline development data.

Stub: entry point only — seeding logic is left to implementers and should be
idempotent so it is safe to re-run.
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    """Seed baseline rows for local development.

    TODO(platform): insert demo users / log sources / sample jobs idempotently.
    """
    raise NotImplementedError


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
