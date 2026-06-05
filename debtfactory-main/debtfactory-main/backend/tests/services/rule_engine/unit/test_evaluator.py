"""Unit tests for the evaluator — eligibility scenarios over the sample matrix."""

from __future__ import annotations

from app.services.rule_engine.engine.evaluator import Evaluator
from app.services.rule_engine.schemas import ApplicantInput


def _applicant(applicants: list[dict], name: str) -> ApplicantInput:
    payload = next(a for a in applicants if a["name"] == name)
    return ApplicantInput(**{k: v for k, v in payload.items() if k != "name"})


def test_clean_high_cibil_eligible_for_multiple_banks(
    evaluator: Evaluator, applicants: list[dict]
) -> None:
    """CIBIL 720 + clean record + income 30k → eligible for multiple banks."""
    results = evaluator.evaluate(_applicant(applicants, "clean_high_cibil"))
    banks = {r.bank_name for r in results}
    assert "BOI" in banks
    assert len(banks) >= 2


def test_underage_excluded_everywhere(evaluator: Evaluator, applicants: list[dict]) -> None:
    """Age 17 → no rule matches (excluded everywhere)."""
    results = evaluator.evaluate(_applicant(applicants, "underage_excluded"))
    assert results == []


def test_pl_written_off_matches_only_write_off_tolerant_rules(
    evaluator: Evaluator, applicants: list[dict]
) -> None:
    """PL written off → only write-off-tolerant (BOM-style) rules match."""
    results = evaluator.evaluate(_applicant(applicants, "pl_written_off"))
    banks = {r.bank_name for r in results}
    # The clean-record banks (which require pl_write_off=false) must be absent.
    assert "BOI" not in banks
    assert "Indian Bank" not in banks


def test_low_income_below_threshold_excluded(evaluator: Evaluator, applicants: list[dict]) -> None:
    """Income below the 25k threshold → excluded from income-gated banks."""
    results = evaluator.evaluate(_applicant(applicants, "low_income_borderline"))
    assert results == []
