"""Rule Engine service exceptions.

All subclass :class:`app.core.exceptions.AppException` so the central handler
renders them into the standard error envelope.
"""

from __future__ import annotations

from app.core.exceptions import AppException


class MatrixParseError(AppException):
    """Raised when the eligibility matrix cannot be read into rows."""

    status_code = 422
    code = "matrix_parse_error"


class RuleValidationError(AppException):
    """Raised when parsed matrix rows fail integrity validation."""

    status_code = 422
    code = "rule_validation_error"


class JdmBuildError(AppException):
    """Raised when rows cannot be assembled into a valid JDM graph."""

    status_code = 500
    code = "jdm_build_error"


class EvaluationError(AppException):
    """Raised when zen-engine fails to evaluate an applicant."""

    status_code = 500
    code = "evaluation_error"
