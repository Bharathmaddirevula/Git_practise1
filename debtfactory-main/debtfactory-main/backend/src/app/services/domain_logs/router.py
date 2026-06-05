"""Domain Logs HTTP router (SSE / WebSocket). Auto-discovered ``router``."""

from __future__ import annotations

from fastapi import APIRouter, Depends, WebSocket
from fastapi.responses import StreamingResponse

from app.services.domain_logs.constants import ROUTE_PREFIX
from app.services.domain_logs.dependencies import get_domain_logs_service
from app.services.domain_logs.service import DomainLogsService

router = APIRouter(prefix=ROUTE_PREFIX, tags=["domain-logs"])


@router.get("/sources/{source_id}/stream")
async def stream_sse(
    source_id: int,
    service: DomainLogsService = Depends(get_domain_logs_service),
) -> StreamingResponse:
    """Stream a log source over Server-Sent Events.  TODO(domain_logs)."""
    raise NotImplementedError


@router.websocket("/sources/{source_id}/ws")
async def stream_ws(
    websocket: WebSocket,
    source_id: int,
    service: DomainLogsService = Depends(get_domain_logs_service),
) -> None:
    """Stream a log source over a WebSocket.  TODO(domain_logs)."""
    raise NotImplementedError
