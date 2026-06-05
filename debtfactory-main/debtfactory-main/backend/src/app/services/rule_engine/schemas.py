"""Rule Engine request/response DTOs (Pydantic v2).

These encode the applicant-profile contract from the Bank Eligibility Matrix.
Field names are the snake_case boundary names defined in :mod:`constants`; they
are mapped to the engine's expected keys in one place before evaluation.

Stubs: shapes are fully declared (so implementers know the exact contract) but no
business validation/logic is added beyond field types.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ApplicantInput(BaseModel):
    """Applicant profile evaluated against every bank rule.

    Each field corresponds to one input column of the decision table. See
    ``README.md`` for the matrix mapping and example ZEN expressions.
    """

    model_config = ConfigDict(extra="forbid")

    cibil_score: int = Field(..., description="CIBIL credit score, e.g. 720.")
    pl_write_off: bool = Field(False, description="Personal loan written off.")
    home_loan_wo: bool = Field(False, description="Home loan written off.")
    consumer_loan_wo: bool = Field(False, description="Consumer loan written off.")
    agri_loan_wo: bool = Field(False, description="Agri loan written off.")
    msme_loan_wo: bool = Field(False, description="MSME loan written off.")
    auto_loan_wo: bool = Field(False, description="Auto loan written off.")
    cc_write_off: bool = Field(False, description="Credit card written off.")
    wo_amount: float = Field(0, description="Total written-off amount.")
    age: int = Field(..., description="Applicant age in years.")
    existing_account: bool = Field(False, description="Holds an existing account.")
    nri_pio: bool = Field(False, description="NRI / PIO status.")
    total_experience: float = Field(0, description="Total work experience (years).")
    current_experience: float = Field(0, description="Current job experience (years).")
    salary_mode: str = Field(..., description='Salary credit mode, e.g. "Bank Credit".')
    income: float = Field(..., description="Monthly net income.")

    # BRE sheet additions. Exact-match booleans: the applicant value must equal
    # the bank's Yes/No cell for the rule to match (same semantics as write-offs).
    existing_car_loan: bool = Field(False, description="Applicant has an existing car loan.")
    rented_house_self_employed: bool = Field(
        False, description="Self-employed applicant living in a rented house."
    )
    agriculture: bool = Field(False, description="Agriculture profession.")
    no_income_proof: bool = Field(False, description="Applicant has no income proof.")
    rental_income_non_itr: bool = Field(False, description="Rental income not declared in ITR.")
    rental_income_not_reflecting: bool = Field(
        False, description="Rental income not reflecting in bank statements."
    )
    itr_not_filed: bool = Field(False, description="Applicant has not filed ITR.")


class EligibilityResult(BaseModel):
    """A single bank the applicant is eligible for."""

    bank_name: str = Field(..., description="Eligible bank name, e.g. BOI.")
    description: str | None = Field(None, description="Optional rule note.")


class EvaluateResponse(BaseModel):
    """Response for ``POST /rule-engine/evaluate``."""

    eligible_banks: list[EligibilityResult]
    matched_rule_count: int = Field(..., description="Number of rules that matched.")


class ReloadResponse(BaseModel):
    """Response for ``POST /rule-engine/reload``."""

    rows_parsed: int
    jdm_path: str
    reloaded: bool = True
