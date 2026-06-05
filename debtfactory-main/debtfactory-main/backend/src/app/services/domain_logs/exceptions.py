"""Domain Logs service exceptions."""

from __future__ import annotations

from app.core.exceptions import AppException


class LogSourceNotFoundError(AppException):
    """Raised when a requested log source does not exist."""

    status_code = 404
    code = "log_source_not_found"


class StreamClosedError(AppException):
    """Raised when a stream is consumed after the source closed."""

    status_code = 409
    code = "stream_closed"
