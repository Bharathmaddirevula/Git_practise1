"""Log collector protocol. Stub: interface only."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from app.services.domain_logs.schemas import LogEntryOut


@runtime_checkable
class LogCollector(Protocol):
    """A source of log entries (file tail, journald, kafka, ...)."""

    name: str

    def collect(self) -> AsyncIterator[LogEntryOut]:
        """Yield entries as they are produced.  TODO(domain_logs)."""
        ...
