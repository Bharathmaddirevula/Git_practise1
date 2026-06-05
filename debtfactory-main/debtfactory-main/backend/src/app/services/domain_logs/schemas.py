"""Domain Logs DTOs (Pydantic v2). Stub: shapes only."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LogSourcePublic(BaseModel):
    """A streamable log source."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class LogEntryOut(BaseModel):
    """A single streamed log line."""

    model_config = ConfigDict(from_attributes=True)

    source_id: int
    level: str
    message: str
    timestamp: datetime
