"""OCR Jobs orchestration layer. Stub: signatures only."""

from __future__ import annotations

from app.services.ocr_jobs.schemas import (
    JobStatusOut,
    JobSubmitRequest,
    OcrResultOut,
)


class OcrJobsService:
    """Coordinates job submission, status polling, and result retrieval."""

    def submit(self, request: JobSubmitRequest) -> JobStatusOut:
        """Create an OcrJob and enqueue the Celery task.

        TODO(ocr_jobs): persist the job, dispatch ``run_ocr`` via Celery.
        """
        raise NotImplementedError

    def status(self, job_id: int) -> JobStatusOut:
        """Return the current status of a job.  TODO(ocr_jobs)."""
        raise NotImplementedError

    def result(self, job_id: int) -> OcrResultOut:
        """Return the extracted text for a completed job.  TODO(ocr_jobs)."""
        raise NotImplementedError
