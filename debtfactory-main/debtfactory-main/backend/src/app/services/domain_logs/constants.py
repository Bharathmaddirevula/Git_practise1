"""Domain Logs service constants."""

from __future__ import annotations

from typing import Final

SERVICE_NAME: Final[str] = "domain_logs"
ROUTE_PREFIX: Final[str] = "/domain-logs"

# Transport identifiers.
TRANSPORT_SSE: Final[str] = "sse"
TRANSPORT_WEBSOCKET: Final[str] = "websocket"

# TODO(domain_logs): heartbeat interval, buffer sizes, retention.
