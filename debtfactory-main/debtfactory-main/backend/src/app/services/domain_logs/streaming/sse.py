"""Server-Sent Events transport. Stub: signatures only."""

from __future__ import annotations

from collections.abc import AsyncIterator

from app.services.domain_logs.schemas import LogEntryOut


async def sse_event_stream(entries: AsyncIterator[LogEntryOut]) -> AsyncIterator[str]:
    """Adapt log entries into SSE ``data:`` frames.  TODO(domain_logs)."""
    raise NotImplementedError
    yield  # pragma: no cover
