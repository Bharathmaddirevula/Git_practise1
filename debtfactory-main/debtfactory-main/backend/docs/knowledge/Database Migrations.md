---
title: Database Migrations
tags: [debtfactory, migrations, sql, postgres]
created: 2026-06-03
updated: 2026-06-03
---

# 🗃️ Database Migrations

**Plain-SQL migration files** (recommended format) applied by a small idempotent
runner. Depends on [[Docker & Data Stores]] being up.

> Switched from Alembic `.py` revisions to `.sql` files on 2026-06-03 (product
> request). The Alembic infra (`alembic.ini`, `migrations/env.py`) is left in
> place but unused for auth/domain_logs.

## Layout

```
migrations/sql/
  auth/0001_init.up.sql          auth/0001_init.down.sql
  domain_logs/0001_init.up.sql   domain_logs/0001_init.down.sql
scripts/migrate_sql.py           # the runner
```

- Each `*.up.sql` is applied **once**, in sorted path order, inside a transaction.
- Applied files are recorded in a **`schema_migrations`** tracking table → re-runs are a no-op (idempotent).
- DB URL comes from app settings / `.env` (the `+asyncpg` suffix is stripped for the raw asyncpg DSN).

## Commands

```powershell
.venv\Scripts\python scripts\migrate_sql.py --status        # applied vs PENDING
.venv\Scripts\python scripts\migrate_sql.py                 # apply all pending *.up.sql
.venv\Scripts\python scripts\migrate_sql.py --down auth/0001_init   # roll back one
```

## What exists today (2026-06-03)

Migrations for **Auth** and **Domain Logs** only:

| Service | File | Tables |
| ------- | ---- | ------ |
| auth | `auth/0001_init.up.sql` | `auth_user`, `auth_credential`, `auth_session` (FK → user, ON DELETE CASCADE) |
| domain_logs | `domain_logs/0001_init.up.sql` | `domain_logs_source`, `domain_logs_entry` (FK → source) |

`rule_engine` and `ocr_jobs` have no migrations yet (intentional).

## Adding a migration

1. Create `migrations/sql/<service>/<NNNN>_<name>.up.sql` (and a matching `.down.sql`).
2. `python scripts/migrate_sql.py` — it picks up the new file and records it.

> Numbering is per-service (`0001`, `0002`, …); runner order is sorted path order.

## Verify

```powershell
docker exec loan-platform-db-1 psql -U loan -d loan_platform -c "\dt"
docker exec loan-platform-db-1 psql -U loan -d loan_platform -c "SELECT * FROM schema_migrations;"
```

#migrations #sql
