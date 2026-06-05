"""OCR Jobs DTOs (Pydantic v2). Stub: shapes only."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobSubmitRequest(BaseModel):
    """Request to enqueue an OCR job for a stored document."""

    model_config = ConfigDict(extra="forbid")

    document_uri: str
    language: str = "eng"


class JobStatusOut(BaseModel):
    """Current status of an OCR job."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime


class OcrResultOut(BaseModel):
    """Extracted text result for a completed job."""

    model_config = ConfigDict(from_attributes=True)

    job_id: int
    text: str
    confidence: float | None = None
