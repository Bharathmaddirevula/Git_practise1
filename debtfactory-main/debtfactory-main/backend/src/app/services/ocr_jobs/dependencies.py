"""OCR Jobs FastAPI dependencies. Stub only."""

from __future__ import annotations

from app.services.ocr_jobs.service import OcrJobsService


def get_ocr_jobs_service() -> OcrJobsService:
    """Provide an :class:`OcrJobsService`.  TODO(ocr_jobs)."""
    raise NotImplementedError
