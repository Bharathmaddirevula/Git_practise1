"""WebSocket transport. Stub: signatures only."""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import WebSocket

from app.services.domain_logs.schemas import LogEntryOut


async def pump_to_websocket(websocket: WebSocket, entries: AsyncIterator[LogEntryOut]) -> None:
    """Forward log entries to a connected WebSocket.  TODO(domain_logs)."""
    raise NotImplementedError
