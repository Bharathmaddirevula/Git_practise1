"""Unit tests for the matrix parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.services.rule_engine.engine.matrix_parser import parse
from app.services.rule_engine.exceptions import MatrixParseError


def test_parses_all_rows(sample_matrix_path: Path) -> None:
    """Every data row in the sample matrix becomes a MatrixRow."""
    rows = parse(sample_matrix_path)
    assert len(rows) >= 1
    # Every row carries a bank_name output and at least the CIBIL input.
    for row in rows:
        assert row.outputs.get("bank_name")
        assert "cibil_score" in row.inputs


def test_blank_cells_mean_unconstrained(sample_matrix_path: Path) -> None:
    """Blank input cells are omitted (treated as no constraint)."""
    rows = parse(sample_matrix_path)
    first = rows[0]
    # Row 1 (BOI) leaves the CC Write Off cell blank -> not present in inputs.
    assert "cc_write_off" not in first.inputs
    # A constrained cell is present and carries its ZEN expression verbatim.
    assert first.inputs["cibil_score"] == ">= 675"


def test_rejects_missing_file(tmp_path: Path) -> None:
    """A non-existent workbook raises MatrixParseError."""
    with pytest.raises(MatrixParseError):
        parse(tmp_path / "does_not_exist.xlsx")
