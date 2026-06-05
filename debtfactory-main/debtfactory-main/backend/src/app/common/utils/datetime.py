"""Timezone-aware datetime helpers (shared).

Stubs only — keep all timestamp handling UTC-first and tz-aware.
"""

from __future__ import annotations

from datetime import datetime


def utc_now() -> datetime:
    """Return the current time as a timezone-aware UTC datetime.

    TODO(common): implement with ``datetime.now(tz=timezone.utc)``.
    """
    raise NotImplementedError


def to_utc(value: datetime) -> datetime:
    """Normalize ``value`` to a timezone-aware UTC datetime.

    TODO(common): assume naive inputs are UTC; convert aware inputs.
    """
    raise NotImplementedError
