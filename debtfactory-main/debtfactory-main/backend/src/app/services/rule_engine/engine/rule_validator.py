"""Stage 2: validate parsed matrix rows for integrity.

Catches authoring mistakes before they reach the JDM builder: unknown columns,
malformed range/comparison syntax, type mismatches (a bool column holding a
number), and rows missing a ``bank_name`` output.
"""

from __future__ import annotations

import re

from app.services.rule_engine.constants import INPUT_FIELDS, OUTPUT_FIELDS
from app.services.rule_engine.engine.matrix_parser import MatrixRow
from app.services.rule_engine.exceptions import RuleValidationError

# Boolean input fields: cells must be a bare ``true`` / ``false``.
_BOOL_FIELDS: frozenset[str] = frozenset(
    {
        "pl_write_off",
        "home_loan_wo",
        "consumer_loan_wo",
        "agri_loan_wo",
        "msme_loan_wo",
        "auto_loan_wo",
        "cc_write_off",
        "existing_account",
        "nri_pio",
        # BRE sheet additions (exact-match booleans).
        "existing_car_loan",
        "rented_house_self_employed",
        "agriculture",
        "no_income_proof",
        "rental_income_non_itr",
        "rental_income_not_reflecting",
        "itr_not_filed",
    }
)

# String input fields: cells must be a quoted string literal, e.g. ``"Bank Credit"``.
_STRING_FIELDS: frozenset[str] = frozenset({"salary_mode"})

# Accepted shapes for numeric ZEN unary tests: ``>= 675``, ``< 5000``, ``[21..70]``,
# ``(0..100]``, or a bare number.
_COMPARISON = re.compile(r"^(>=|<=|>|<|==|!=)\s*-?\d+(\.\d+)?$")
_RANGE = re.compile(r"^[\[(]\s*-?\d+(\.\d+)?\s*\.\.\s*-?\d+(\.\d+)?\s*[\])]$")
_BARE_NUMBER = re.compile(r"^-?\d+(\.\d+)?$")
_QUOTED_STRING = re.compile(r'^".*"$')


def validate_rows(rows: list[MatrixRow]) -> None:
    """Validate every row, raising on the first integrity violation.

    Args:
        rows: Parsed rows from :func:`matrix_parser.parse`.

    Raises:
        RuleValidationError: on unknown columns, bad ZEN expression syntax,
            type mismatches, or a missing required output.
    """
    if not rows:
        raise RuleValidationError("No rules parsed from the matrix.")

    valid_inputs = set(INPUT_FIELDS)
    valid_outputs = set(OUTPUT_FIELDS)

    for row in rows:
        for field_name, expr in row.inputs.items():
            if field_name not in valid_inputs:
                raise RuleValidationError(
                    f"Row {row.index}: unknown input field {field_name!r}.",
                    details={"row": row.index, "field": field_name},
                )
            _validate_input_cell(row.index, field_name, expr)

        for field_name in row.outputs:
            if field_name not in valid_outputs:
                raise RuleValidationError(
                    f"Row {row.index}: unknown output field {field_name!r}.",
                    details={"row": row.index, "field": field_name},
                )

        bank_name = row.outputs.get("bank_name", "").strip()
        if not bank_name:
            raise RuleValidationError(
                f"Row {row.index}: missing required output 'bank_name'.",
                details={"row": row.index},
            )


def _validate_input_cell(row_index: int, field_name: str, expr: str) -> None:
    """Validate a single input cell's ZEN expression against its field type."""
    if field_name in _BOOL_FIELDS:
        if expr not in ("true", "false"):
            raise RuleValidationError(
                f"Row {row_index}: boolean field {field_name!r} expects "
                f"'true'/'false', got {expr!r}.",
                details={"row": row_index, "field": field_name, "value": expr},
            )
        return

    if field_name in _STRING_FIELDS:
        if not _QUOTED_STRING.match(expr):
            raise RuleValidationError(
                f"Row {row_index}: string field {field_name!r} expects a quoted "
                f'literal like "Bank Credit", got {expr!r}.',
                details={"row": row_index, "field": field_name, "value": expr},
            )
        return

    # Otherwise numeric: comparison, range, or bare number.
    if not (_COMPARISON.match(expr) or _RANGE.match(expr) or _BARE_NUMBER.match(expr)):
        raise RuleValidationError(
            f"Row {row_index}: numeric field {field_name!r} has malformed " f"expression {expr!r}.",
            details={"row": row_index, "field": field_name, "value": expr},
        )
