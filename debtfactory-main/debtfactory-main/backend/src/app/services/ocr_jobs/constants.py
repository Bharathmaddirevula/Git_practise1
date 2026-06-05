"""OCR Jobs service constants."""

from __future__ import annotations

from typing import Final

SERVICE_NAME: Final[str] = "ocr_jobs"
ROUTE_PREFIX: Final[str] = "/ocr-jobs"

# Job status values.
STATUS_PENDING: Final[str] = "pending"
STATUS_RUNNING: Final[str] = "running"
STATUS_SUCCEEDED: Final[str] = "succeeded"
STATUS_FAILED: Final[str] = "failed"

# Celery task name.
TASK_RUN_OCR: Final[str] = "ocr_jobs.run_ocr"

# TODO(ocr_jobs): supported mime types, size limits.
