# Loan Platform Backend

A **feature-sliced modular monolith**: one FastAPI application hosting four
self-contained feature services, built so multiple teams ship in parallel with
**minimal merge conflicts**.

| Service | Path | Status |
| ------- | ---- | ------ |
| Rule Engine | `src/app/services/rule_engine` | ✅ **implemented** — zen-engine eligibility decisioning |
| Auth | `src/app/services/auth` | 🟡 stubbed + DB schema |
| Domain Logs | `src/app/services/domain_logs` | 🟡 stubbed + DB schema |
| OCR Jobs | `src/app/services/ocr_jobs` | 🟡 stubbed (Celery + Redis) |

**Stack:** FastAPI · SQLAlchemy (async) · Pydantic v2 · PostgreSQL 16 · Redis 7 ·
zen-engine (GoRules JDM) · Celery · Docker · **Python 3.12**.

---

## Quickstart (Docker — no local Python)

> You only need **Docker Desktop** + **git**. There is **no local Python or venv** —
> the whole team runs the same image, so "works on my machine" goes away.

```powershell
copy .env.example .env          # Unix/Mac: cp .env.example .env
```

Then use the task runner — `.\dev.ps1 <cmd>` on Windows, `make <cmd>` on Mac/Linux/WSL:

| Windows | Mac/Linux | Does |
| ------- | --------- | ---- |
| `.\dev.ps1 up` | `make up` | build + start **api, db, redis, adminer** (hot reload) |
| `.\dev.ps1 test` | `make test` | run the test suite in a container |
| `.\dev.ps1 check` | `make check` | lint + types + tests (**exactly what CI runs**) |
| `.\dev.ps1 migrate` | `make migrate` | apply SQL migrations |
| `.\dev.ps1 shell` | `make shell` | shell into the dev image |

- API → <http://localhost:8000> · docs → <http://localhost:8000/docs>
- DB UI (Adminer) → <http://localhost:8081> (Server `db`, user/pass `loan`, db `loan_platform`)

Prefer raw Docker? Every command above is just:

```bash
docker compose -f compose.yaml -f compose.dev.yaml up --build db redis adminer api
docker compose -f compose.yaml -f compose.dev.yaml run --rm --no-deps api pytest -q
```

> Full walkthrough (testing, Rule Engine, team workflow):
> [`docs/workflow.md`](docs/workflow.md). New here? Start with
> [`TEAM_ONBOARDING.md`](TEAM_ONBOARDING.md).

---

## Docker & the database UI

| Service | Container | Host port | Notes |
| ------- | --------- | --------- | ----- |
| Postgres | `loan-platform-db-1` | **5433** → 5432 | host 5432 is often taken by a native Postgres |
| Redis | `loan-platform-redis-1` | **6379** | |
| Adminer (DB web UI) | `loan-platform-adminer-1` | **8081** → 8080 | browse the DB in your browser |

**Open the database in a browser:** in Docker Desktop click the **`8081`** port (or
open <http://localhost:8081>) and log in — **System** `PostgreSQL`, **Server** `db`,
**User** `loan`, **Password** `loan`, **Database** `loan_platform`. (Use `db`, not
`localhost` — Adminer runs inside Docker.)

```powershell
docker compose -f compose.yaml -f compose.dev.yaml up -d db redis adminer   # start stores
docker compose -f compose.yaml -f compose.dev.yaml down                     # stop
docker compose -f compose.yaml -f compose.dev.yaml down -v                  # stop + wipe data
```

---

## Database migrations (plain SQL)

Migrations are **`.sql` files** applied by an idempotent runner (tracked in a
`schema_migrations` table). See [`docs/knowledge/Database Migrations.md`](docs/knowledge/Database%20Migrations.md).

```powershell
.\dev.ps1 migrate          # apply pending (make migrate). Auto-runs on `up`.
docker compose -f compose.yaml -f compose.dev.yaml run --rm api python scripts/migrate_sql.py --status
docker compose -f compose.yaml -f compose.dev.yaml run --rm api python scripts/migrate_sql.py --down auth/0001_init
```

Files live in `migrations/sql/<service>/NNNN_<name>.{up,down}.sql`. Auth + Domain
Logs schemas exist today. The API container also applies migrations on startup.

---

## Rule Engine

Turns `Bank_Eligibility_Matrix.xlsx` (**8 banks, 23 input params**) into eligibility
decisions via **GoRules zen-engine**. Regenerate the JDM artifact with
`.\dev.ps1 jdm` (`make jdm`).

```powershell
curl -X POST http://localhost:8000/rule-engine/evaluate `
  -H "Content-Type: application/json" `
  -d '{
    "cibil_score": 750, "pl_write_off": false, "home_loan_wo": false,
    "consumer_loan_wo": false, "agri_loan_wo": false, "msme_loan_wo": false,
    "auto_loan_wo": false, "cc_write_off": false, "wo_amount": 0, "age": 30,
    "existing_account": true, "nri_pio": false, "total_experience": 5,
    "current_experience": 2, "salary_mode": "Bank Credit", "income": 50000,
    "existing_car_loan": true, "rented_house_self_employed": false,
    "agriculture": false, "no_income_proof": false, "rental_income_non_itr": false,
    "rental_income_not_reflecting": false, "itr_not_filed": false
  }'
```

The 7 BRE flags are **exact-match**, which partitions banks into disjoint groups:

| Group | Banks | Profile |
| ----- | ----- | ------- |
| A | BOI, Indian Bank, IOB | car loan + strict docs |
| B | BOB | no car loan + self-employed renting |
| C | HDFC, AXIS, Kotak | full lenient-doc profile |
| D | BOM | PL **and** CC written off |

- **Verified test data:** [`docs/test_scenarios.md`](docs/test_scenarios.md)
- **Postman collection:** `postman/DebtFactory-RuleEngine.postman_collection.json` (import → Run)
- **Service contract:** [`src/app/services/rule_engine/README.md`](src/app/services/rule_engine/README.md)

---

## Testing & quality gates

All gates run **inside the dev container** — identical versions to CI:

```powershell
.\dev.ps1 check                                  # ruff + black + mypy + pytest  (make check)
.\dev.ps1 test                                   # tests only                    (make test)
.\dev.ps1 test tests/services/rule_engine        # a subset
```

CI builds the **same image** and runs the **same commands**, so green locally ⇒ green in CI.

---

## Project layout

```
src/app/
├── main.py            # app factory; mounts health + auto-discovered routers
├── api/               # router auto-discovery, health/readiness
├── core/              # config, database, logging, errors, middleware
├── common/            # shared schemas + utils (the only cross-service sharing)
└── services/<slice>/  # one self-contained vertical slice per feature
migrations/sql/        # plain-SQL migrations (per service)
scripts/migrate_sql.py # the migration runner
postman/               # importable API test collection
docs/knowledge/        # Obsidian knowledge vault
```

See [`docs/architecture.md`](docs/architecture.md) for the rationale.

---

## Team workflow & CI/CD

**Trunk-based development**, short-lived branches, Conventional Commits, per-service
ownership. Adding a service touches **zero** shared files (routers/settings are
auto-discovered).

👉 **Start here for Git + CI/CD:** [`docs/ci_cd_guide.md`](docs/ci_cd_guide.md) —
first push, branch protection, the PR pipeline, reading CI failures, and deploys.

```
branch  →  push  →  PR  →  CI (ruff·black·mypy·pytest·migrations)  →  review  →  squash-merge  →  CD
```

---

## Documentation map

| Doc | What |
| --- | ---- |
| [`TEAM_ONBOARDING.md`](TEAM_ONBOARDING.md) | 5-phase checklist for new developers |
| [`docs/workflow.md`](docs/workflow.md) | Complete runbook (setup, testing, Rule Engine) |
| [`docs/ci_cd_guide.md`](docs/ci_cd_guide.md) | Git + CI/CD for the team ⭐ |
| [`docs/git_workflow.md`](docs/git_workflow.md) | Branch/commit/merge conventions |
| [`docs/architecture.md`](docs/architecture.md) | Design rationale & request lifecycle |
| [`docs/service_template.md`](docs/service_template.md) | Add a new service (no shared files) |
| [`docs/knowledge/`](docs/knowledge/Index.md) | Obsidian knowledge vault (decisions, troubleshooting) |
