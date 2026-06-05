---
title: Troubleshooting Log
tags: [debtfactory, troubleshooting, errors, postman]
created: 2026-06-03
---

# 🩺 Troubleshooting Log

Every error hit during development, with the root cause and fix. Newest-relevant first.

## `POST /rule-engine/evaluate` errors

### 422 — `type: missing`, fields like `cibil_score`
- **Cause:** request body uses **camelCase** (`cibil`, `salaryMode`) but the schema is **snake_case** with `extra="forbid"`.
- **Fix:** send snake_case field names. See `docs/test_scenarios.md` for the exact body. Mapping table in [[Rule Engine]].

### 422 — `model_attributes_type`, input is the whole JSON as a string
- **Cause:** request **Content-Type is not `application/json`** (Postman Body→raw left as *Text* → `text/plain`). FastAPI then hands the raw text to the validator instead of parsing it.
- **Fix:** Postman → Body → raw → dropdown **JSON** (sets `Content-Type: application/json`).

### 500 — `TypeError: Object of type bytes is not JSON serializable`
- **Cause (real bug, fixed):** the validation-error handler called `json.dumps` on `exc.errors()`, which contains the **raw request `bytes`** when the JSON body is malformed.
- **Fix:** wrap handlers in `jsonable_encoder` (`src/app/core/exceptions.py`) — same as FastAPI's built-in handler. Malformed JSON now returns a clean 422.

## Startup / env errors

### `ModuleNotFoundError: No module named 'app'`
- **Cause:** `src` not on `sys.path`; the bash-style `PYTHONPATH=src` prefix is a no-op in PowerShell.
- **Fix:** `pip install -e .` (best) or `$env:PYTHONPATH="src"`. See [[Environment & Tooling]].

### `pip install -e .` → `requires a different Python: 3.13.x not in '<3.13'`
- **Cause:** venv built on Python 3.13; project pins `<3.13`.
- **Fix:** rebuild the venv on **3.12.8**. See [[Environment & Tooling]].

### Corrupted venv: `ModuleNotFoundError: pip._internal.cli`
- **Cause:** `pip install --upgrade pip` in place — Defender locked pip's vendor files mid-rewrite.
- **Fix:** recreate the venv, **don't** self-upgrade pip; install other packages with the bundled pip.

### `Remove-Item .venv` → `Access denied: _greenlet…pyd`
- **Cause:** a running `uvicorn --reload` process held the DLL.
- **Fix:** kill the venv python process, then delete.

## Docker

### Port already allocated (5432)
- **Cause:** a native Postgres already listens on host 5432.
- **Fix:** publish docker Postgres on **5433** (see [[Docker & Data Stores]]).

## zen-engine

### `create_decision(...)` → `bytes object cannot be converted to 'Mapping'`
- **Cause:** passed JSON bytes/str; v0.53 wants a **dict**.
- **Fix:** `engine.create_decision(jdm_dict)`.

#troubleshooting #errors
