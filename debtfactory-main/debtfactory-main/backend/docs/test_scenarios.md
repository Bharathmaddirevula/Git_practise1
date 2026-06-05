# Rule Engine - Test Scenarios

Verified against the live engine and `Bank_Eligibility_Matrix.xlsx` (8 banks, 23 input params). Endpoint: `POST /rule-engine/evaluate`.

> **BRE flags are exact-match.** The 7 BRE columns (existing_car_loan, rented_house_self_employed, agriculture, no_income_proof, rental_income_non_itr, rental_income_not_reflecting, itr_not_filed) require the applicant value to **equal** the bank's Yes/No cell. This splits banks into disjoint groups: **BOI/Indian Bank/IOB** (car loan + strict docs), **BOB** (no car loan + self-employed renting), **HDFC/AXIS/Kotak** (full lenient-doc profile), **BOM** (PL+CC written off).

## How to use

- **Postman:** import `postman/DebtFactory-RuleEngine.postman_collection.json`, set `baseUrl`, *Run collection*. Each request asserts its expected banks.

- **Manual:** each payload is the base applicant with the listed field(s) changed. Send header `Content-Type: application/json`.


## Base applicant (BOI / Indian Bank / IOB group)

```json
{
  "cibil_score": 750,
  "pl_write_off": false,
  "home_loan_wo": false,
  "consumer_loan_wo": false,
  "agri_loan_wo": false,
  "msme_loan_wo": false,
  "auto_loan_wo": false,
  "cc_write_off": false,
  "wo_amount": 0,
  "age": 30,
  "existing_account": true,
  "nri_pio": false,
  "total_experience": 5,
  "current_experience": 2,
  "salary_mode": "Bank Credit",
  "income": 50000,
  "existing_car_loan": true,
  "rented_house_self_employed": false,
  "agriculture": false,
  "no_income_proof": false,
  "rental_income_non_itr": false,
  "rental_income_not_reflecting": false,
  "itr_not_filed": false
}
```


## Positive scenarios

| ID | Category | Change from base | Expected banks (count) |
| -- | -------- | ---------------- | ---------------------- |
| S01 | Happy path | _(none - base)_ | **3** - BOI, Indian Bank, IOB |
| S02 | Happy path | `existing_car_loan=False`, `rented_house_self_employed=True` | **1** - BOB |
| S03 | Happy path | full lenient profile + `cibil_score=720`, `age=40` | **3** - HDFC, AXIS, Kotak |
| S04 | Happy path | full lenient profile + `pl_write_off=True`, `cc_write_off=True`, `cibil_score=660`, `wo_amount=3000` | **1** - BOM |
| S05 | CIBIL | `cibil_score=649` | **0** - _none_ |
| S06 | CIBIL | `cibil_score=674` | **0** - _none_ |
| S07 | CIBIL | `cibil_score=675` | **2** - BOI, IOB |
| S08 | CIBIL | `cibil_score=724` | **2** - BOI, IOB |
| S09 | CIBIL | `cibil_score=725` | **3** - BOI, Indian Bank, IOB |
| S10 | Age | `age=17` | **0** - _none_ |
| S11 | Age | `age=18` | **1** - Indian Bank |
| S12 | Age | `age=20` | **1** - Indian Bank |
| S13 | Age | `age=21` | **3** - BOI, Indian Bank, IOB |
| S14 | Age | `age=70` | **3** - BOI, Indian Bank, IOB |
| S15 | Age | `age=71` | **0** - _none_ |
| S16 | Write-offs | `home_loan_wo=True` | **0** - _none_ |
| S17 | Write-offs | `consumer_loan_wo=True` | **0** - _none_ |
| S18 | Write-offs | `agri_loan_wo=True` | **0** - _none_ |
| S19 | Write-offs | `msme_loan_wo=True` | **0** - _none_ |
| S20 | Write-offs | `auto_loan_wo=True` | **0** - _none_ |
| S21 | Write-offs | `pl_write_off=True` | **0** - _none_ |
| S22 | Write-offs | `cc_write_off=True` | **1** - BOI |
| S23 | WO amount | `wo_amount=4999` | **3** - BOI, Indian Bank, IOB |
| S24 | WO amount | `wo_amount=5000` | **2** - Indian Bank, IOB |
| S25 | Account/NRI | `existing_account=False` | **1** - IOB |
| S26 | Account/NRI | `nri_pio=True` | **2** - Indian Bank, IOB |
| S27 | Exp/Salary/Income | `total_experience=1` | **0** - _none_ |
| S28 | Exp/Salary/Income | `current_experience=0` | **0** - _none_ |
| S29 | Exp/Salary/Income | `salary_mode=Cash` | **0** - _none_ |
| S30 | Exp/Salary/Income | `income=24999` | **0** - _none_ |
| S31 | BRE flags | `existing_car_loan=False` | **0** - _none_ |
| S32 | BRE flags | `rented_house_self_employed=True` | **0** - _none_ |
| S33 | BRE flags | `agriculture=True` | **0** - _none_ |
| S34 | BRE flags | `no_income_proof=True` | **0** - _none_ |
| S35 | BRE flags | `itr_not_filed=True` | **0** - _none_ |
| S36 | BRE flags | `rental_income_non_itr=True` | **0** - _none_ |

## Validation / error scenarios (expect 422)

| ID | Case | Expected |
| -- | ---- | -------- |
| E01 | Missing required field (no cibil_score) | HTTP 422, `error.code=validation_error` |
| E02 | Wrong type (age as string) | HTTP 422, `error.code=validation_error` |
| E03 | Unknown/extra field (extra=forbid) | HTTP 422, `error.code=validation_error` |
| E04 | Empty body | HTTP 422, `error.code=validation_error` |

## Full payloads for the four bank groups

### S01 - Strict-doc applicant (car loan, ITR) - BOI/Indian/IOB group  ->  (3) BOI, Indian Bank, IOB

```json
{
  "cibil_score": 750,
  "pl_write_off": false,
  "home_loan_wo": false,
  "consumer_loan_wo": false,
  "agri_loan_wo": false,
  "msme_loan_wo": false,
  "auto_loan_wo": false,
  "cc_write_off": false,
  "wo_amount": 0,
  "age": 30,
  "existing_account": true,
  "nri_pio": false,
  "total_experience": 5,
  "current_experience": 2,
  "salary_mode": "Bank Credit",
  "income": 50000,
  "existing_car_loan": true,
  "rented_house_self_employed": false,
  "agriculture": false,
  "no_income_proof": false,
  "rental_income_non_itr": false,
  "rental_income_not_reflecting": false,
  "itr_not_filed": false
}
```

### S02 - BOB group: no car loan + self-employed renting  ->  (1) BOB

```json
{
  "cibil_score": 750,
  "pl_write_off": false,
  "home_loan_wo": false,
  "consumer_loan_wo": false,
  "agri_loan_wo": false,
  "msme_loan_wo": false,
  "auto_loan_wo": false,
  "cc_write_off": false,
  "wo_amount": 0,
  "age": 30,
  "existing_account": true,
  "nri_pio": false,
  "total_experience": 5,
  "current_experience": 2,
  "salary_mode": "Bank Credit",
  "income": 50000,
  "existing_car_loan": false,
  "rented_house_self_employed": true,
  "agriculture": false,
  "no_income_proof": false,
  "rental_income_non_itr": false,
  "rental_income_not_reflecting": false,
  "itr_not_filed": false
}
```

### S03 - HDFC/AXIS/Kotak group: full lenient-doc profile  ->  (3) HDFC, AXIS, Kotak

```json
{
  "cibil_score": 720,
  "pl_write_off": false,
  "home_loan_wo": false,
  "consumer_loan_wo": false,
  "agri_loan_wo": false,
  "msme_loan_wo": false,
  "auto_loan_wo": false,
  "cc_write_off": false,
  "wo_amount": 0,
  "age": 40,
  "existing_account": true,
  "nri_pio": false,
  "total_experience": 5,
  "current_experience": 2,
  "salary_mode": "Bank Credit",
  "income": 50000,
  "existing_car_loan": true,
  "rented_house_self_employed": true,
  "agriculture": true,
  "no_income_proof": true,
  "rental_income_non_itr": true,
  "rental_income_not_reflecting": true,
  "itr_not_filed": true
}
```

### S04 - BOM: PL+CC written off (car loan kept true)  ->  (1) BOM

```json
{
  "cibil_score": 660,
  "pl_write_off": true,
  "home_loan_wo": false,
  "consumer_loan_wo": false,
  "agri_loan_wo": false,
  "msme_loan_wo": false,
  "auto_loan_wo": false,
  "cc_write_off": true,
  "wo_amount": 3000,
  "age": 30,
  "existing_account": true,
  "nri_pio": false,
  "total_experience": 5,
  "current_experience": 2,
  "salary_mode": "Bank Credit",
  "income": 50000,
  "existing_car_loan": true,
  "rented_house_self_employed": false,
  "agriculture": false,
  "no_income_proof": false,
  "rental_income_non_itr": false,
  "rental_income_not_reflecting": false,
  "itr_not_filed": false
}
```

