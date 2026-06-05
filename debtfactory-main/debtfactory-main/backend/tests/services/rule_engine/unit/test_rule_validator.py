"""Unit tests for the rule validator."""

from __future__ import annotations

import pytest

from app.services.rule_engine.engine.matrix_parser import MatrixRow
from app.services.rule_engine.engine.rule_validator import validate_rows
from app.services.rule_engine.exceptions import RuleValidationError


def _good_row(**overrides: object) -> MatrixRow:
    inputs = {"cibil_score": ">= 675", "age": "[21..70]"}
    outputs = {"bank_name": '"BOI"'}
    row = MatrixRow(index=1, inputs=dict(inputs), outputs=dict(outputs))
    for key, value in overrides.items():
        if key == "inputs":
            row.inputs = value  # type: ignore[assignment]
        elif key == "outputs":
            row.outputs = value  # type: ignore[assignment]
    return row


def test_accepts_valid_rows() -> None:
    """A well-formed row passes validation without raising."""
    validate_rows([_good_row()])


def test_flags_unknown_columns() -> None:
    """An unrecognized input field raises RuleValidationError."""
    row = _good_row(inputs={"unknown_field": ">= 1"})
    with pytest.raises(RuleValidationError):
        validate_rows([row])


def test_flags_bad_range_syntax() -> None:
    """A malformed range like [21..] raises RuleValidationError."""
    row = _good_row(inputs={"cibil_score": ">= 675", "age": "[21..]"})
    with pytest.raises(RuleValidationError):
        validate_rows([row])


def test_flags_type_mismatch() -> None:
    """A number in a boolean column raises RuleValidationError."""
    row = _good_row(inputs={"cibil_score": ">= 675", "pl_write_off": "5"})
    with pytest.raises(RuleValidationError):
        validate_rows([row])


def test_requires_bank_name_output() -> None:
    """A row missing bank_name raises RuleValidationError."""
    row = _good_row(outputs={"description": '"note"'})
    with pytest.raises(RuleValidationError):
        validate_rows([row])


def test_empty_rows_rejected() -> None:
    """An empty rule set raises RuleValidationError."""
    with pytest.raises(RuleValidationError):
        validate_rows([])
