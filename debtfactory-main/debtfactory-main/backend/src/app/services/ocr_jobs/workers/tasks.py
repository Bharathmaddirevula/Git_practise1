"""Celery task signatures for OCR. Stub: signatures only."""

from __future__ import annotations


def run_ocr(job_id: int) -> None:
    """Run OCR for ``job_id`` and persist the result.

    Registered as the Celery task ``ocr_jobs.run_ocr``.

    TODO(ocr_jobs): load the document, run the engine, store the OcrResult,
    update job status. Decorate with ``@celery_app.task(name=TASK_RUN_OCR)``.
    """
    raise NotImplementedError
