"""Domain Logs orchestration layer. Stub: signatures only."""

from __future__ import annotations

from collections.abc import AsyncIterator

from app.services.domain_logs.schemas import LogEntryOut


class DomainLogsService:
    """Coordinates collectors and streaming transports."""

    async def stream(self, source_id: int) -> AsyncIterator[LogEntryOut]:
        """Yield log entries for ``source_id`` as they arrive.

        TODO(domain_logs): subscribe to the collector and yield entries.
        """
        raise NotImplementedError
        yield  # pragma: no cover  (marks this an async generator)
