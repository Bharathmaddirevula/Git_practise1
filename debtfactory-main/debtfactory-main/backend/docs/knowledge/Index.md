---
title: DebtFactory Backend — Knowledge Index
tags: [moc, debtfactory, backend]
created: 2026-06-03
---

# 🗂️ DebtFactory Backend — Knowledge Map

A Map-of-Content (MOC) for this repo's accumulated knowledge. Open in Obsidian;
every `[[link]]` jumps to a focused note.

## Notes

- [[Rule Engine]] — zen-engine, the Bank Eligibility Matrix → JDM pipeline, the 8-bank model.
- [[Environment & Tooling]] — Python 3.12 venv, editable install, the gotchas that bite on Windows.
- [[Docker & Data Stores]] — Postgres + Redis containers, the host-port map, connection strings.
- [[Database Migrations]] — Alembic multi-branch (per-service) scheme, how to run it.
- [[Troubleshooting Log]] — every error hit so far and its root-cause fix.
- [[Decisions]] — architectural choices made and *why*.

## System at a glance

- **Architecture:** feature-sliced modular monolith — one FastAPI app, 4 vertical service slices (`rule_engine`, `auth`, `domain_logs`, `ocr_jobs`).
- **Auto-discovery:** routers/settings/migrations are discovered by convention — adding a service touches zero shared files.
- **Stack:** FastAPI · SQLAlchemy async · Pydantic v2 · Postgres 16 · Redis 7 · Alembic · zen-engine (GoRules JDM) · Celery.
- **Python:** 3.12.8 only (pin `>=3.12,<3.13`).

## Quick commands

```bash
# data stores
docker compose -f compose.yaml -f compose.dev.yaml up -d db redis
# migrations (note the plural 'heads')
.venv\Scripts\python -m alembic upgrade heads
# run API (editable install => no PYTHONPATH needed)
.venv\Scripts\python -m uvicorn app.main:create_app --factory --reload
# tests + gates
.venv\Scripts\python -m pytest -q
```

#index #debtfactory
