# Claude Code — Repository Scaffolding Prompt

> **Role:** You are a Senior Software Architect + DevOps Engineer.
> **Goal:** Generate a highly structured, enterprise-grade **Python FastAPI** backend
> monorepo (a *modular monolith*) that hosts four independent feature services and is
> explicitly designed for parallel development by a multi-member team with **minimal
> merge conflicts**.
>
> **Scope of this task:** Scaffold the **complete folder structure and stub files only**.
> Do **not** implement business logic. Every `.py` module gets a module docstring, the
> relevant imports, and clearly-named empty functions/classes with `...` or
> `raise NotImplementedError` bodies plus `# TODO(<service>):` markers. Config, Docker,
> CI, and docs files are fully written (these are infrastructure, not business logic).

---

## 1. Operating Rules

1. Read the companion `skill.md` **before** writing any file. It defines the coding
   standards, architecture invariants, and tooling config you must honor.
2. Produce the tree exactly as specified in §4. Create **every** `__init__.py`. Do not
   omit, rename, or "improve" paths without stating why first.
3. Stub files must be syntactically valid and import-clean (`python -c "import app.main"`
   must succeed once dependencies are installed).
4. Prefer **convention over central registration**. Never create a file that every
   service must edit to register itself (see §3). This is the single most important
   rule for keeping feature branches conflict-free.
5. After scaffolding, run the verification checklist in §8 and report results.

---

## 2. Tech Stack (pin major versions in `pyproject.toml`)

| Concern              | Choice                                                        |
| -------------------- | ------------------------------------------------------------- |
| Language             | Python 3.12                                                   |
| Web framework        | FastAPI + Uvicorn (dev) / Gunicorn+Uvicorn workers (prod)     |
| Data / ORM           | SQLAlchemy 2.x (async) + Alembic                              |
| Validation/Settings  | Pydantic v2 + pydantic-settings                               |
| Rule engine          | `zen-engine` (GoRules JDM, MIT licensed) for the Rule Engine  |
| Background jobs       | Celery + Redis (OCR Jobs Service)                            |
| Containerization     | Docker (multi-stage) + Docker Compose (dev & prod overrides)  |
| Lint / format / type | Ruff + Black + Mypy, orchestrated by pre-commit               |
| Tests                | Pytest + pytest-asyncio + coverage                            |

---

## 3. Anti-Merge-Conflict Architecture (read carefully)

The repo is a **feature-sliced modular monolith**. Each service lives in one
self-contained directory that a single sub-team owns. Apply these patterns so two
teams almost never touch the same file:

- **Router auto-discovery.** `app/api/router_registry.py` walks `app/services/*/router.py`
  and mounts every module-level `router` object. Adding a service therefore touches
  **zero** shared files. There is no hand-maintained "include every router here" list.
- **Settings composition.** Each service ships its own `config.py` exposing a
  `Settings` fragment with a unique env prefix (e.g. `RULE_ENGINE_`, `AUTH_`).
  `app/core/settings_registry.py` discovers and composes them. No global settings file
  is edited per service.
- **Per-service dependencies.** Each service declares its own requirements fragment in
  `requirements/services/<service>.in`. The root pins are compiled, but day-to-day a
  team edits only its own fragment.
- **Per-service DB migrations.** Use Alembic **branch labels** with one version
  subdirectory per service (`migrations/versions/<service>/`). Teams generate revisions
  on their own branch label, avoiding a single linear history that collides constantly.
- **Ownership is codified.** `.github/CODEOWNERS` maps each `app/services/<service>/`
  path to its owning team so reviews route automatically.
- **Service isolation.** A service may depend on `app/core` and `app/common`, but
  **never** imports another service directly. Cross-service needs go through a
  published interface in `common/` or an event/queue. State this in PRs.

---

## 4. Target Directory Tree

Create exactly this. `# stub` = empty boilerplate (docstring + signatures only).
`# full` = write complete, working infrastructure content.

```text
loan-platform-backend/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                      # full: lint + type + test matrix, per-service paths-filter
│   │   ├── cd.yml                      # full: build & push images, deploy gates
│   │   └── pr-labeler.yml              # full: auto-label PRs by changed service path
│   ├── CODEOWNERS                      # full: map services/<x>/ -> @team-x
│   └── pull_request_template.md        # full: checklist incl. "no cross-service imports"
├── .vscode/
│   └── settings.json                   # full: ruff/black/mypy on save, pytest rootdir
├── docker/
│   ├── api/
│   │   ├── Dockerfile                  # full: multi-stage base→dev→prod
│   │   └── entrypoint.sh               # full: run migrations then launch server
│   ├── postgres/
│   │   └── init.sql                    # full: create db + extensions
│   └── redis/
│       └── redis.conf                  # full: dev-safe defaults
├── compose.yaml                        # full: base stack (api, db, redis)
├── compose.dev.yaml                    # full: hot-reload, source bind-mounts, debug ports
├── compose.prod.yaml                   # full: gunicorn workers, no bind-mounts, healthchecks
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py                     # full: app factory; calls router_registry
│       ├── api/
│       │   ├── __init__.py
│       │   ├── router_registry.py      # full: auto-discover services/*/router.py
│       │   └── health.py               # full: /health, /readyz
│       ├── core/                       # shared infrastructure (no business logic)
│       │   ├── __init__.py
│       │   ├── config.py               # full: base Settings + env loading
│       │   ├── settings_registry.py    # full: compose per-service Settings fragments
│       │   ├── database.py             # full: async engine + session dependency
│       │   ├── logging.py              # full: structured JSON logging setup
│       │   ├── security.py             # stub: password hashing / token helpers
│       │   ├── middleware.py           # full: request-id, timing, error envelope
│       │   ├── exceptions.py           # full: base AppException + handlers
│       │   └── pagination.py           # stub: shared pagination params/schema
│       ├── common/
│       │   ├── __init__.py
│       │   ├── schemas/
│       │   │   ├── __init__.py
│       │   │   └── base.py             # stub: ORMBase, ResponseEnvelope
│       │   └── utils/
│       │       ├── __init__.py
│       │       └── datetime.py         # stub: tz-aware helpers
│       └── services/
│           ├── __init__.py
│           │
│           ├── rule_engine/            # ── PRIMARY SERVICE (zen-engine) ──
│           │   ├── __init__.py
│           │   ├── router.py           # stub: POST /rule-engine/evaluate, /reload
│           │   ├── schemas.py          # stub: ApplicantInput, EligibilityResult (see §5)
│           │   ├── models.py           # stub: EvaluationAudit ORM model
│           │   ├── service.py          # stub: orchestration layer
│           │   ├── dependencies.py     # stub: provide loaded engine
│           │   ├── exceptions.py       # stub: MatrixParseError, RuleValidationError
│           │   ├── constants.py        # stub: column→field name map, defaults
│           │   ├── config.py           # stub: RuleEngineSettings (RULE_ENGINE_ prefix)
│           │   ├── engine/
│           │   │   ├── __init__.py
│           │   │   ├── matrix_parser.py    # stub: Bank_Eligibility_Matrix.xlsx → rows
│           │   │   ├── jdm_builder.py       # stub: rows → GoRules JDM graph JSON
│           │   │   ├── rule_validator.py    # stub: validate matrix & JDM integrity
│           │   │   └── evaluator.py         # stub: wrap zen.ZenEngine, evaluate()
│           │   ├── decisions/
│           │   │   └── .gitkeep             # generated JDM lands here (git-ignored output)
│           │   ├── data/
│           │   │   └── Bank_Eligibility_Matrix.xlsx   # copy the source matrix here
│           │   └── README.md           # full: service contract + JDM mapping (§5)
│           │
│           ├── auth/                   # ── MULTI-CHANNEL AUTH ──
│           │   ├── __init__.py
│           │   ├── router.py           # stub
│           │   ├── schemas.py          # stub
│           │   ├── models.py           # stub: User, Credential, Session
│           │   ├── service.py          # stub
│           │   ├── dependencies.py     # stub: current_user, channel resolver
│           │   ├── exceptions.py       # stub
│           │   ├── constants.py        # stub
│           │   ├── config.py           # stub: AuthSettings (AUTH_ prefix)
│           │   ├── channels/
│           │   │   ├── __init__.py
│           │   │   ├── base.py         # stub: AuthChannel protocol
│           │   │   ├── email_password.py   # stub
│           │   │   ├── otp_sms.py           # stub
│           │   │   ├── oauth_google.py      # stub
│           │   │   └── magic_link.py        # stub
│           │   ├── tokens/
│           │   │   ├── __init__.py
│           │   │   ├── jwt.py          # stub
│           │   │   └── refresh.py      # stub
│           │   └── README.md           # full
│           │
│           ├── domain_logs/            # ── LIVE DOMAIN LOGS ──
│           │   ├── __init__.py
│           │   ├── router.py           # stub: SSE/WS stream endpoints
│           │   ├── schemas.py          # stub
│           │   ├── models.py           # stub: LogSource, LogEntry
│           │   ├── service.py          # stub
│           │   ├── dependencies.py     # stub
│           │   ├── exceptions.py       # stub
│           │   ├── constants.py        # stub
│           │   ├── config.py           # stub: DomainLogsSettings (DOMAIN_LOGS_ prefix)
│           │   ├── streaming/
│           │   │   ├── __init__.py
│           │   │   ├── sse.py          # stub: server-sent events
│           │   │   ├── websocket.py    # stub
│           │   │   └── tailer.py       # stub: tail/poll a log source
│           │   ├── collectors/
│           │   │   ├── __init__.py
│           │   │   └── base.py         # stub: LogCollector protocol
│           │   └── README.md           # full
│           │
│           └── ocr_jobs/               # ── OCR JOBS ──
│               ├── __init__.py
│               ├── router.py           # stub: submit job, poll status, fetch result
│               ├── schemas.py          # stub
│               ├── models.py           # stub: OcrJob, OcrResult
│               ├── service.py          # stub
│               ├── dependencies.py     # stub
│               ├── exceptions.py       # stub
│               ├── constants.py        # stub
│               ├── config.py           # stub: OcrSettings (OCR_ prefix)
│               ├── workers/
│               │   ├── __init__.py
│               │   ├── celery_app.py   # stub: celery instance factory
│               │   └── tasks.py        # stub: run_ocr task signature
│               ├── engines/
│               │   ├── __init__.py
│               │   └── base.py         # stub: OcrEngine protocol (tesseract/cloud)
│               ├── storage/
│               │   ├── __init__.py
│               │   └── base.py         # stub: artifact store protocol
│               └── README.md           # full
├── migrations/
│   ├── env.py                          # full: async Alembic env, multi-branch aware
│   ├── script.py.mako                  # full
│   └── versions/
│       ├── rule_engine/.gitkeep        # per-service branch label dir
│       ├── auth/.gitkeep
│       ├── domain_logs/.gitkeep
│       └── ocr_jobs/.gitkeep
├── tests/
│   ├── __init__.py
│   ├── conftest.py                     # full: app/client/db fixtures
│   ├── core/
│   │   └── test_health.py              # full: smoke test for /health
│   └── services/
│       ├── rule_engine/                # ── TEST CASES REQUIRED (§6) ──
│       │   ├── __init__.py
│       │   ├── conftest.py             # stub: engine + sample matrix fixtures
│       │   ├── unit/
│       │   │   ├── test_matrix_parser.py    # stub w/ named test fns + TODO
│       │   │   ├── test_jdm_builder.py       # stub
│       │   │   ├── test_rule_validator.py    # stub
│       │   │   └── test_evaluator.py         # stub: eligibility scenarios
│       │   ├── integration/
│       │   │   └── test_eligibility_api.py   # stub: POST /evaluate happy/edge paths
│       │   └── fixtures/
│       │       ├── sample_matrix.xlsx        # small fixture matrix (copy/trim source)
│       │       └── applicants.json           # sample applicant payloads
│       ├── auth/__init__.py
│       ├── domain_logs/__init__.py
│       └── ocr_jobs/__init__.py
├── scripts/
│   ├── generate_jdm.py                 # stub: CLI matrix.xlsx → decisions/*.jdm.json
│   ├── seed_db.py                      # stub
│   └── compile_requirements.sh         # full: pip-compile all fragments
├── docs/
│   ├── architecture.md                 # full: modular-monolith rationale, diagrams
│   ├── git_workflow.md                 # full: branch strategy (§7)
│   ├── service_template.md             # full: "how to add a new service" checklist
│   └── adr/
│       └── 0001-modular-monolith.md    # full: the ADR that records this decision
├── requirements/
│   ├── base.in                         # full: fastapi, uvicorn, sqlalchemy, pydantic…
│   ├── dev.in                          # full: ruff, black, mypy, pytest…
│   └── services/
│       ├── rule_engine.in              # full: zen-engine, openpyxl
│       ├── auth.in                     # full: passlib, pyjwt, authlib
│       ├── domain_logs.in              # full: sse-starlette, websockets
│       └── ocr_jobs.in                 # full: celery, redis, pytesseract
├── .env.example                        # full: every env var, grouped by service prefix
├── .gitignore                          # full
├── .dockerignore                       # full
├── .pre-commit-config.yaml             # full: ruff, black, mypy, end-of-file-fixer
├── pyproject.toml                      # full: project metadata + tool configs (§ skill.md)
├── Makefile                            # full: up/down/test/lint/migrate/jdm targets
└── README.md                           # full: quickstart, layout, team workflow
```

---

## 5. Rule Engine Service — Contract & Matrix Mapping

The source `Bank_Eligibility_Matrix.xlsx` is a **GoRules JDM decision table**: each row
is a rule whose input cells are ZEN Expression Language conditions, and whose output is
the eligible **Bank Name**. The scaffold must encode this contract (in `schemas.py`,
`constants.py`, and the service `README.md`) so implementers know the exact shape.

**Input fields (applicant profile) — column → field → example expression**

| Matrix column     | Field (`schemas.py`)  | Type    | Example cell expr |
| ----------------- | --------------------- | ------- | ----------------- |
| CIBIL Score       | `cibil_score`         | int     | `>= 675`          |
| PL Write Off      | `pl_write_off`        | bool    | `false`           |
| Home Loan WO      | `home_loan_wo`        | bool    | `false`           |
| Consumer Loan WO  | `consumer_loan_wo`    | bool    | `false`           |
| Agri Loan WO      | `agri_loan_wo`        | bool    | `false`           |
| MSME Loan WO      | `msme_loan_wo`        | bool    | `false`           |
| Auto Loan WO      | `auto_loan_wo`        | bool    | `false`           |
| CC Write Off      | `cc_write_off`        | bool    | `false`           |
| WO Amount         | `wo_amount`           | number  | `< 5000`          |
| Age               | `age`                 | int     | `[21..70]`        |
| Existing A/C      | `existing_account`    | bool    | `true`            |
| NRI/PIO           | `nri_pio`             | bool    | `false`           |
| Total Exp         | `total_experience`    | number  | `>= 2`            |
| Current Exp       | `current_experience`  | number  | `>= 1`            |
| Salary Mode       | `salary_mode`         | str     | `"Bank Credit"`   |
| Income            | `income`              | number  | `>= 25000`        |

**Output fields**

| Matrix column | Field          | Type |
| ------------- | -------------- | ---- |
| Bank Name     | `bank_name`    | str  |
| Description   | `description`  | str  |

**Data flow the stubs must express (signatures only, no logic):**

```
Bank_Eligibility_Matrix.xlsx
        │  matrix_parser.parse()         -> list[MatrixRow]
        ▼
   rule_validator.validate_rows()        -> raises RuleValidationError on bad cells
        │
        ▼
   jdm_builder.build()                   -> GoRules JDM graph (dict / JSON)
        │  (persisted to decisions/bank_eligibility.jdm.json)
        ▼
   evaluator.Evaluator(zen.ZenEngine)    -> .evaluate(ApplicantInput) -> list[EligibilityResult]
        ▲
   service.py  ── called by ──  router.py  POST /rule-engine/evaluate
```

`evaluator.py` must reference the real `zen-engine` API in its docstring so the
implementer wires it correctly:

```python
import zen
engine = zen.ZenEngine()
decision = engine.create_decision(jdm_json_content)
result = decision.evaluate(applicant_dict)  # -> {"result": {...}}
```

`router.py` endpoints to stub: `POST /rule-engine/evaluate` (applicant → eligible banks)
and `POST /rule-engine/reload` (re-parse matrix → rebuild JDM at runtime).

---

## 6. Test Cases (Rule Engine) — stub but name them

Create the test files with realistic, **named but unimplemented** test functions
(`def test_...(): ... # TODO`). At minimum:

- `test_matrix_parser.py`: parses all rows; handles blank cells; rejects malformed sheet.
- `test_jdm_builder.py`: produces a valid JDM graph with one rule per matrix row.
- `test_rule_validator.py`: flags unknown columns, bad range syntax, type mismatches.
- `test_evaluator.py`: scenario coverage — e.g. *CIBIL 720 + clean record + income 30k →
  eligible for multiple banks*; *age 17 → excluded everywhere*; *PL written off →
  only BOM-style rules match*.
- `integration/test_eligibility_api.py`: `POST /evaluate` returns 200 + bank list for a
  valid applicant; 422 on a malformed payload.

Add `fixtures/applicants.json` with 3–4 sample profiles and a trimmed
`fixtures/sample_matrix.xlsx` so tests don't depend on the production matrix.

---

## 7. Git Branch Strategy (also write to `docs/git_workflow.md`)

Adopt **trunk-based development with short-lived feature branches**:

- `main` — always deployable; protected; merges only via PR with green CI + 1 CODEOWNER approval.
- `develop` *(optional)* — integration branch if the team prefers a staging gate.
- Feature branches: `feat/<service>/<ticket>-<slug>`, e.g. `feat/rule-engine/RUL-12-matrix-parser`.
- Other prefixes: `fix/`, `chore/`, `docs/`, `refactor/`, `test/`.
- **Scope a branch to one service directory** wherever possible — this is what makes the
  feature-sliced layout pay off; two teams editing two service folders never collide.
- Commits follow **Conventional Commits** (`feat(rule-engine): ...`), enforced by a
  commit-msg pre-commit hook.
- Rebase feature branches on `main` before merge; **squash-merge** to keep history linear.
- DB changes: generate Alembic revisions under your service's branch label only.

---

## 8. Verification Checklist (run and report)

1. `tree -a -I '.git'` matches §4.
2. `find . -name '__init__.py' | wc -l` — every package dir has one.
3. `python -c "import sys; sys.path.insert(0,'src'); import app.main"` succeeds (after
   `pip install -r requirements/base.txt`).
4. `ruff check . && black --check . && mypy src` pass on the stubs (stubs must be clean).
5. `pytest -q` collects the test tree (collected, even if skipped/TODO).
6. `docker compose -f compose.yaml -f compose.dev.yaml config` validates.
7. Confirm **no** file requires per-service editing to register a router, settings
   fragment, or migration head.

Report each item as ✅/❌ with a one-line note. Stop and ask if any §3 invariant would
have to be violated to proceed.
