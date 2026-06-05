"""Unit tests for the JDM builder."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.services.rule_engine.engine import jdm_builder, matrix_parser
from app.services.rule_engine.engine.matrix_parser import MatrixRow
from app.services.rule_engine.exceptions import JdmBuildError


def test_builds_valid_jdm_graph(sample_matrix_path: Path) -> None:
    """build() returns a JDM dict with input/table/output nodes wired."""
    rows = matrix_parser.parse(sample_matrix_path)
    graph = jdm_builder.build(rows)

    node_types = [node["type"] for node in graph["nodes"]]
    assert node_types == ["inputNode", "decisionTableNode", "outputNode"]
    # Two edges wire input -> table -> output.
    assert len(graph["edges"]) == 2


def test_one_rule_per_matrix_row(sample_matrix_path: Path) -> None:
    """The decision table has exactly one row per matrix rule."""
    rows = matrix_parser.parse(sample_matrix_path)
    graph = jdm_builder.build(rows)
    table = graph["nodes"][1]["content"]
    assert len(table["rules"]) == len(rows)
    assert table["hitPolicy"] == "collect"


def test_output_columns_mapped(sample_matrix_path: Path) -> None:
    """bank_name/description outputs are emitted per rule as ZEN literals."""
    rows = matrix_parser.parse(sample_matrix_path)
    graph = jdm_builder.build(rows)
    table = graph["nodes"][1]["content"]
    output_fields = {col["field"] for col in table["outputs"]}
    assert {"bank_name", "description"} <= output_fields
    # The first rule's bank_name is a quoted ZEN string literal.
    assert table["rules"][0]["o_bank_name"].startswith('"')


def test_empty_rows_rejected() -> None:
    """Building from zero rows raises JdmBuildError."""
    with pytest.raises(JdmBuildError):
        jdm_builder.build([])


def test_blank_input_cell_becomes_empty_string() -> None:
    """An unconstrained input field maps to an empty table cell."""
    row = MatrixRow(index=1, inputs={"cibil_score": ">= 675"}, outputs={"bank_name": '"BOI"'})
    graph = jdm_builder.build([row])
    rule = graph["nodes"][1]["content"]["rules"][0]
    assert rule["i_cibil_score"] == ">= 675"
    assert rule["i_age"] == ""  # not constrained -> blank
