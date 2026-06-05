"""OCR Jobs HTTP router. Auto-discovered ``router``."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.services.ocr_jobs.constants import ROUTE_PREFIX
from app.services.ocr_jobs.dependencies import get_ocr_jobs_service
from app.services.ocr_jobs.schemas import (
    JobStatusOut,
    JobSubmitRequest,
    OcrResultOut,
)
from app.services.ocr_jobs.service import OcrJobsService

router = APIRouter(prefix=ROUTE_PREFIX, tags=["ocr-jobs"])


@router.post("/jobs", response_model=JobStatusOut, status_code=status.HTTP_202_ACCEPTED)
async def submit_job(
    request: JobSubmitRequest,
    service: OcrJobsService = Depends(get_ocr_jobs_service),
) -> JobStatusOut:
    """Enqueue an OCR job.  TODO(ocr_jobs)."""
    raise NotImplementedError


@router.get("/jobs/{job_id}", response_model=JobStatusOut)
async def get_job_status(
    job_id: int,
    service: OcrJobsService = Depends(get_ocr_jobs_service),
) -> JobStatusOut:
    """Poll a job's status.  TODO(ocr_jobs)."""
    raise NotImplementedError


@router.get("/jobs/{job_id}/result", response_model=OcrResultOut)
async def get_job_result(
    job_id: int,
    service: OcrJobsService = Depends(get_ocr_jobs_service),
) -> OcrResultOut:
    """Fetch a completed job's extracted text.  TODO(ocr_jobs)."""
    raise NotImplementedError
