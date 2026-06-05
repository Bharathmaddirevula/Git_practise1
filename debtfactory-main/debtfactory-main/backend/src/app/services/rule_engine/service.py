"""Rule Engine orchestration layer.

Coordinates the pipeline (parse -> validate -> build -> evaluate) and the JDM
build artifact lifecycle. Framework-agnostic: the router calls into here; this
module never touches HTTP.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.services.rule_engine.constants import JDM_OUTPUT_FILENAME
from app.services.rule_engine.engine import jdm_builder, matrix_parser, rule_validator
from app.services.rule_engine.engine.evaluator import Evaluator
from app.services.rule_engine.engine.jdm_builder import JdmGraph
from app.services.rule_engine.schemas import ApplicantInput, EligibilityResult


def build_jdm_from_matrix(matrix_path: Path) -> tuple[JdmGraph, int]:
    """Run parse -> validate -> build and return the JDM graph and row count."""
    rows = matrix_parser.parse(matrix_path)
    rule_validator.validate_rows(rows)
    graph = jdm_builder.build(rows)
    return graph, len(rows)


def build_evaluator_from_matrix(matrix_path: Path) -> Evaluator:
    """Build a ready-to-use :class:`Evaluator` straight from the matrix."""
    graph, _ = build_jdm_from_matrix(matrix_path)
    return Evaluator(graph)


class RuleEngineService:
    """Application service for eligibility evaluation and matrix reloads."""

    def __init__(self, evaluator: Evaluator) -> None:
        self._evaluator = evaluator

    def evaluate(self, applicant: ApplicantInput) -> list[EligibilityResult]:
        """Evaluate one applicant and return eligible banks."""
        return self._evaluator.evaluate(applicant)

    @staticmethod
    def reload_matrix(matrix_path: Path, decisions_dir: Path) -> tuple[int, Path]:
        """Re-parse the matrix, rebuild the JDM artifact, return (rows, path).

        Runs parse -> validate -> build and writes the JDM JSON to
        ``decisions_dir``. Used by the ``/reload`` endpoint and the
        ``generate_jdm`` script.
        """
        graph, row_count = build_jdm_from_matrix(matrix_path)
        decisions_dir.mkdir(parents=True, exist_ok=True)
        jdm_path = decisions_dir / JDM_OUTPUT_FILENAME
        jdm_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
        return row_count, jdm_path
