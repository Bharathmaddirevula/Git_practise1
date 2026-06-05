---
title: Rule Engine
tags: [debtfactory, rule-engine, zen-engine, jdm]
created: 2026-06-03
---

# ⚙️ Rule Engine

Eligibility decisioning over the **Bank Eligibility Matrix**, powered by
[`zen-engine`](https://gorules.io) (GoRules JDM). See also [[Decisions]].

## Pipeline

```
Bank_Eligibility_Matrix.xlsx
  → matrix_parser.parse()        (openpyxl → list[MatrixRow])
  → rule_validator.validate_rows (type/range/bank_name checks)
  → jdm_builder.build()          (GoRules JDM graph, hitPolicy=collect)
  → Evaluator(zen.ZenEngine)     (.evaluate(ApplicantInput) → eligible banks)
```

Source of truth = the **xlsx**. Regenerate the JDM artifact:
`python scripts/generate_jdm.py` (writes `decisions/bank_eligibility.jdm.json`).
Never hand-edit the JDM.

## zen-engine API (v0.53)

```python
import zen
engine = zen.ZenEngine()
decision = engine.create_decision(jdm_dict)   # takes a dict (NOT bytes/str)
decision.evaluate({...})                       # -> {"result": [...]} with collect
```

## The matrix

- **8 banks:** BOI, Indian Bank, IOB, BOB, HDFC, AXIS, Kotak, BOM.
- **23 input params** (16 original + 7 from the [[Decisions|BRE sheet]]) + 2 outputs (Bank Name, Description).
- Blank input cell = **no constraint**. Cell values are ZEN expressions (`>= 675`, `[21..70]`, `"Bank Credit"`, `true`).

### Exact-match groups (consequence of the [[Decisions|exact-match choice]])

The BRE flags split banks into **disjoint** profiles — no single applicant matches across groups:

| Group | Banks | Profile |
| ----- | ----- | ------- |
| A | BOI, Indian Bank, IOB | car loan + strict docs (all lenient flags false) |
| B | BOB | no car loan + self-employed renting |
| C | HDFC, AXIS, Kotak | full lenient-doc profile (agri, no-proof, no-ITR…) |
| D | BOM | PL **and** CC written off (both required), CIBIL ≥ 650, age 21–60 |

> ⚠️ **BOM needs BOTH `pl_write_off=true` AND `cc_write_off=true`** — `pl_write_off` alone yields zero banks.
> ⚠️ Under exact-match, a plain salaried applicant with no car loan qualifies for **nothing** (BOI/Indian/IOB require `existing_car_loan=true`).

## Testing

- Verified scenarios live in `docs/test_scenarios.md` and the importable Postman collection `postman/DebtFactory-RuleEngine.postman_collection.json`.
- See [[Troubleshooting Log]] for the request-shape errors (camelCase, content-type).

#rule-engine #zen-engine
