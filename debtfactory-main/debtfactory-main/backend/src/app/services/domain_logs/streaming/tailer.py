"""Tail/poll a log source into an async stream. Stub: signatures only."""

from __future__ import annotations

from collections.abc import AsyncIterator

from app.services.domain_logs.schemas import LogEntryOut


async def tail(source_id: int) -> AsyncIterator[LogEntryOut]:
    """Yield new entries for ``source_id`` as they appear.  TODO(domain_logs)."""
    raise NotImplementedError
    yield  # pragma: no cover
