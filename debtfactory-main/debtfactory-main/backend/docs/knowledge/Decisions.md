---
title: Decisions
tags: [debtfactory, adr, decisions]
created: 2026-06-03
---

# 🧭 Decisions

Architectural / product choices made, with rationale. Complements the formal ADR
in `docs/adr/`.

## BRE flags use exact-match semantics
- **Date:** 2026-06-03
- **Context:** added 7 discriminating params from the BRE sheet (Existing Car Loan, Rented-House-Self-Employed, Agriculture, No Income Proof, ITR Not Filed, 2× Rental-Income) to the matrix.
- **Options:** (A) *tolerance* — BRE "No" excludes that attribute, "Yes" = no constraint; (B) *exact-match* — applicant value must equal the bank's Yes/No.
- **Decision:** **(B) exact-match**, chosen by the product owner after seeing the trade-off.
- **Consequence:** banks split into disjoint groups (see [[Rule Engine]]); a normal salaried applicant **without** a car loan matches **zero** banks because BOI/Indian/IOB require `existing_car_loan=true`. Flip to tolerance is a small change (matrix cells `true→blank` for "Yes" + regen JDM) if ever needed.

## Scope: discriminating params only
- Added only the 7 BRE params that **differ between banks** (and thus change eligibility).
- Skipped ~20 params that are identical across all 8 banks (Loan enquiry, Unmarried, employment types, …) — they never change the outcome. Easy to add later for completeness.

## Rule source of truth: Excel now, Postgres later
- **Now:** keep the **xlsx** as source of truth (credit team authors it; pipeline parses → validates → builds JDM). Add a CI gate that runs `rule_validator` on every commit.
- **Later (trigger):** first need for live rule edits, audit/change-log, or non-engineer management → promote **Postgres** to system-of-record with the xlsx as an import/export format. Migration is cheap because only the *parse* stage changes; validation + JDM build + zen-engine are source-agnostic.

## Migrations: per-service Alembic branches
- Each service owns an independent branch label + version dir; upgrade with `alembic upgrade heads`. See [[Database Migrations]].
- Auth + Domain Logs migrations exist; rule_engine + ocr_jobs deferred.

## Python 3.12, editable install
- Pin `>=3.12,<3.13`; venv on 3.12.8; `pip install -e .` so no `PYTHONPATH` juggling. See [[Environment & Tooling]].

#decisions #adr
