"""Application exception hierarchy and central handlers.

Services raise typed exceptions subclassing :class:`AppException`; the handlers
registered here render every error into one consistent JSON envelope so callers
get a uniform shape regardless of which service failed. Avoid scattering ad-hoc
``HTTPException`` strings — subclass :class:`AppException` instead.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base class for all domain errors.

    Attributes:
        status_code: HTTP status the central handler should return.
        code: Stable machine-readable error code (e.g. ``"rule_validation"``).
        message: Human-readable description.
        details: Optional structured context for the client.
    """

    status_code: int = 500
    code: str = "internal_error"

    def __init__(
        self,
        message: str | None = None,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


def _envelope(code: str, message: str, details: dict[str, Any]) -> dict[str, Any]:
    """Build the standard error envelope body."""
    return {"error": {"code": code, "message": message, "details": details}}


def register_exception_handlers(app: FastAPI) -> None:
    """Attach handlers that render errors into the standard envelope."""

    @app.exception_handler(AppException)
    async def _handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            # jsonable_encoder guards against non-serializable values in details.
            content=jsonable_encoder(_envelope(exc.code, exc.message, exc.details)),
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        # exc.errors() can contain bytes (raw body on malformed JSON) or exception
        # objects (in ``ctx``); jsonable_encoder coerces them to JSON-safe values.
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder(
                _envelope(
                    "validation_error",
                    "Request validation failed.",
                    {"errors": exc.errors()},
                )
            ),
        )
