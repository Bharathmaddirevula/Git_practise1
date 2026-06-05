"""Rule Engine test fixtures: sample matrix + applicant payloads.

Tests must not depend on the production matrix — they use the trimmed
``fixtures/sample_matrix.xlsx`` and ``fixtures/applicants.json`` instead.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_matrix_path() -> Path:
    """Path to the trimmed sample matrix workbook."""
    return _FIXTURES / "sample_matrix.xlsx"


@pytest.fixture
def applicants() -> list[dict]:
    """Sample applicant payloads keyed by the ``name`` field."""
    return json.loads((_FIXTURES / "applicants.json").read_text(encoding="utf-8"))


@pytest.fixture
def evaluator(sample_matrix_path: Path):
    """Provide a loaded Evaluator over the sample matrix."""
    from app.services.rule_engine.service import build_evaluator_from_matrix

    return build_evaluator_from_matrix(sample_matrix_path)
