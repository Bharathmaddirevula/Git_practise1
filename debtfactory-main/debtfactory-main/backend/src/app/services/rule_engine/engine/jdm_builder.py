"""Stage 3: assemble validated rows into a GoRules JDM graph.

Produces the JDM document zen-engine consumes: an input node, a single
``decisionTable`` node whose rows are the matrix rules (input cells are ZEN
condition strings, output cells are bank literals), and an output node, wired
input -> table -> output.

The resulting dict is JSON-serialized to ``decisions/bank_eligibility.jdm.json``
as a build artifact.
"""

from __future__ import annotations

from typing import Any

from app.services.rule_engine.constants import (
    INPUT_COLUMN_TO_FIELD,
    OUTPUT_COLUMN_TO_FIELD,
)
from app.services.rule_engine.engine.matrix_parser import MatrixRow
from app.services.rule_engine.exceptions import JdmBuildError

# A JDM document is a plain JSON-able mapping.
JdmGraph = dict[str, Any]

_INPUT_NODE_ID = "input_node"
_TABLE_NODE_ID = "decision_table"
_OUTPUT_NODE_ID = "output_node"


def build(rows: list[MatrixRow]) -> JdmGraph:
    """Build a GoRules JDM decision graph from validated matrix rows.

    Args:
        rows: Validated rows (one rule each).

    Returns:
        A JDM graph dict with ``nodes`` and ``edges``, ready to serialize and
        hand to ``zen.ZenEngine``.

    Raises:
        JdmBuildError: if a graph cannot be assembled from the rows.
    """
    if not rows:
        raise JdmBuildError("Cannot build a JDM graph from zero rows.")

    # Stable input/output column ids, derived from the canonical field order so
    # the generated artifact is deterministic.
    input_defs = [
        {"id": f"i_{field_name}", "name": column, "field": field_name}
        for column, field_name in INPUT_COLUMN_TO_FIELD.items()
    ]
    output_defs = [
        {"id": f"o_{field_name}", "name": column, "field": field_name}
        for column, field_name in OUTPUT_COLUMN_TO_FIELD.items()
    ]

    table_rules: list[dict[str, str]] = []
    for row in rows:
        rule: dict[str, str] = {"_id": f"rule_{row.index}"}
        for col in input_defs:
            field_name = col["field"]
            # Blank cell (absent) == no constraint == empty string in the table.
            rule[col["id"]] = row.inputs.get(field_name, "")
        for col in output_defs:
            field_name = col["field"]
            value = row.outputs.get(field_name, "")
            # Outputs are ZEN expressions; emit a quoted literal when the author
            # supplied a bare (unquoted) string, leave already-quoted as-is.
            rule[col["id"]] = _as_output_expression(value)
        table_rules.append(rule)

    table_content = {
        "hitPolicy": "collect",
        "inputs": input_defs,
        "outputs": output_defs,
        "rules": table_rules,
    }

    return {
        "contentType": "application/vnd.gorules.decision",
        "nodes": [
            {
                "id": _INPUT_NODE_ID,
                "type": "inputNode",
                "name": "Applicant",
                "position": {"x": 0, "y": 0},
            },
            {
                "id": _TABLE_NODE_ID,
                "type": "decisionTableNode",
                "name": "Bank Eligibility",
                "position": {"x": 300, "y": 0},
                "content": table_content,
            },
            {
                "id": _OUTPUT_NODE_ID,
                "type": "outputNode",
                "name": "Eligible Banks",
                "position": {"x": 600, "y": 0},
            },
        ],
        "edges": [
            {
                "id": "edge_in_table",
                "sourceId": _INPUT_NODE_ID,
                "targetId": _TABLE_NODE_ID,
                "type": "edge",
            },
            {
                "id": "edge_table_out",
                "sourceId": _TABLE_NODE_ID,
                "targetId": _OUTPUT_NODE_ID,
                "type": "edge",
            },
        ],
    }


def _as_output_expression(value: str) -> str:
    """Return a ZEN output expression for a raw output cell value.

    Already-quoted values (``"BOI"``) pass through; bare strings are wrapped in
    quotes; blank stays blank.
    """
    if value == "":
        return ""
    if value.startswith('"') and value.endswith('"'):
        return value
    escaped = value.replace('"', '\\"')
    return f'"{escaped}"'
