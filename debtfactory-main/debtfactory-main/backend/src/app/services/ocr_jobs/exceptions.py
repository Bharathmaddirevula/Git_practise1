"""OCR Jobs service exceptions."""

from __future__ import annotations

from app.core.exceptions import AppException


class JobNotFoundError(AppException):
    """Raised when a job id is unknown."""

    status_code = 404
    code = "job_not_found"


class UnsupportedDocumentError(AppException):
    """Raised when an uploaded document type is not supported."""

    status_code = 415
    code = "unsupported_document"


class OcrEngineError(AppException):
    """Raised when the OCR engine fails to process a document."""

    status_code = 500
    code = "ocr_engine_error"
