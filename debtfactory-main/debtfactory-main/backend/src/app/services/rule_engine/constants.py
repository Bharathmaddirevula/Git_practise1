"""Rule Engine constants: the matrix column contract and defaults.

This module is the single place that maps the ``Bank_Eligibility_Matrix.xlsx``
column headers to the snake_case field names used on the Python boundary. Keep
the mapping here so parser/validator/builder all agree on names and so a column
rename is a one-line change.

The matrix is a GoRules JDM decision table: each input cell holds a ZEN
Expression Language condition (e.g. ``>= 675``, ``[21..70]``, ``"Bank Credit"``)
evaluated against the applicant field of the same column.
"""

from __future__ import annotations

from typing import Final

# Service-wide identifiers.
SERVICE_NAME: Final[str] = "rule_engine"
ROUTE_PREFIX: Final[str] = "/rule-engine"

# Where the parsed JDM build artifact is written / loaded from.
MATRIX_SHEET_NAME: Final[str] = "decision table"
JDM_OUTPUT_FILENAME: Final[str] = "bank_eligibility.jdm.json"

# Input columns: matrix header -> applicant field name. Order matters — it is the
# left-to-right column order of the decision table.
INPUT_COLUMN_TO_FIELD: Final[dict[str, str]] = {
    "CIBIL Score": "cibil_score",
    "PL Write Off": "pl_write_off",
    "Home Loan WO": "home_loan_wo",
    "Consumer Loan WO": "consumer_loan_wo",
    "Agri Loan WO": "agri_loan_wo",
    "MSME Loan WO": "msme_loan_wo",
    "Auto Loan WO": "auto_loan_wo",
    "CC Write Off": "cc_write_off",
    "WO Amount": "wo_amount",
    "Age": "age",
    "Existing A/C": "existing_account",
    "NRI/PIO": "nri_pio",
    "Total Exp": "total_experience",
    "Current Exp": "current_experience",
    "Salary Mode": "salary_mode",
    "Income": "income",
    # BRE sheet additions (exact-match boolean flags).
    "Existing Car Loan": "existing_car_loan",
    "Rented House SE": "rented_house_self_employed",
    "Agriculture": "agriculture",
    "No Income Proof": "no_income_proof",
    "Rental Income Non-ITR": "rental_income_non_itr",
    "Rental Income Not Reflecting": "rental_income_not_reflecting",
    "ITR Not Filed": "itr_not_filed",
}

# Output columns: matrix header -> result field name.
OUTPUT_COLUMN_TO_FIELD: Final[dict[str, str]] = {
    "Bank Name": "bank_name",
    "Description": "description",
}

# Convenience views.
INPUT_FIELDS: Final[tuple[str, ...]] = tuple(INPUT_COLUMN_TO_FIELD.values())
OUTPUT_FIELDS: Final[tuple[str, ...]] = tuple(OUTPUT_COLUMN_TO_FIELD.values())
ALL_COLUMNS: Final[tuple[str, ...]] = (
    *INPUT_COLUMN_TO_FIELD.keys(),
    *OUTPUT_COLUMN_TO_FIELD.keys(),
)
