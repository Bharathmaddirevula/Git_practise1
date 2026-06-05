---
name: loan-platform-backend
description: >-
  Coding standards, architecture invariants, and tooling rules for the FastAPI
  loan-platform modular-monolith backend. Use this skill whenever working in this
  repository — scaffolding or editing any feature service (rule_engine, auth,
  domain_logs, ocr_jobs), wiring FastAPI routers, writing Pydantic schemas or
  SQLAlchemy models, configuring Docker/Compose, adding Alembic migrations, or
  setting up lint/type/test config. Apply it even when the request seems narrow
  (e.g. "add an endpoint" or "write a test"), because the layout is optimized for
  conflict-free parallel team development and small changes can quietly break that.
---

# Loan Platform Backend — Engineering Skill

This repository is a **feature-sliced modular monolith**: one FastAPI app, four
self-contained feature services, built so multiple teams ship in parallel with
minimal merge conflicts. Honor the invariants below in everything you generate.

## Architecture invariants (non-negotiable)

1. **Vertical slices.** All code for a feature lives under
   `src/app/services/<service>/`. A service owns its `router`, `schemas`, `models`,
   `service`, `dependencies`, `exceptions`, `constants`, and `config`.
2. **Dependency direction is one-way.** `services/*` may import from `app.core` and
   `app.common`. They must **never** import from another service. Shared contracts go
   in `app/common/`; cross-service runtime coupling goes through a queue/event, not a
   direct import. If a task seems to need a service→service import, stop and surface it.
3. **No central registration files.** Routers are auto-discovered
   (`app/api/router_registry.py` scans `services/*/router.py` for a module-level
   `router`). Settings fragments are auto-composed (`app/core/settings_registry.py`).
   Never reintroduce a hand-edited "list every router/setting/migration here" file —
   that is the merge-conflict hotspot this design removes.
4. **Config is per-service and prefixed.** Each `config.py` defines a `pydantic-settings`
   model with a unique env prefix (`RULE_ENGINE_`, `AUTH_`, `DOMAIN_LOGS_`, `OCR_`).
   Add new env vars to that fragment and to `.env.example` under the right group.
5. **Migrations are branch-labeled per service.** Generate Alembic revisions into
   `migrations/versions/<service>/` under that service's branch label. Do not create
   cross-service revisions.

## Layered responsibilities within a service

Keep these layers distinct; do not collapse them:

- `router.py` — HTTP only: path/verb, status codes, request/response models, calls
  `service`. No business logic, no direct DB access.
- `service.py` — orchestration and business rules; depends on repositories/engine
  helpers; framework-agnostic where practical.
- `schemas.py` — Pydantic v2 request/response DTOs. Never expose ORM models directly.
- `models.py` — SQLAlchemy ORM only.
- `dependencies.py` — FastAPI `Depends` providers (auth, sessions, loaded engine).
- `exceptions.py` — service-specific exceptions subclassing `app.core.exceptions.AppException`.

## Python & FastAPI coding standards

- Target **Python 3.12**; full type hints on every public function/method.
- **Async-first**: async route handlers, async SQLAlchemy sessions, `httpx.AsyncClient`
  for outbound calls. Never block the event loop with sync I/O.
- Pydantic **v2** idioms (`model_config = ConfigDict(...)`, `field_validator`). Validate
  at the boundary; pass typed models inward.
- Inject collaborators via FastAPI `Depends` — no module-level singletons holding
  request state, no hidden globals.
- Errors raise typed exceptions caught by the central handler in `app/core/exceptions.py`,
  which renders a consistent JSON envelope. Don't scatter ad-hoc `HTTPException` strings.
- Naming: modules/functions/vars `snake_case`, classes `PascalCase`, constants
  `UPPER_SNAKE`. Files use the role name (`router.py`, `service.py`) — don't prefix with
  the service name (the directory already namespaces it).

## Rule Engine specifics (zen-engine)

- The rule engine wraps **`zen-engine`** (GoRules JDM, MIT). Pipeline:
  `matrix_parser` (xlsx → rows) → `rule_validator` (integrity) → `jdm_builder`
  (rows → JDM graph) → `evaluator` (loads JDM into `zen.ZenEngine`, evaluates applicants).
- Treat the parsed JDM as a build artifact: write it to `decisions/*.jdm.json`, keep the
  source of truth in `data/Bank_Eligibility_Matrix.xlsx`, and expose a `reload` path.
- Field names and types must match the matrix contract documented in the service
  `README.md` and `prompt.md` (`cibil_score`, write-off booleans, `age` range,
  `income`, `salary_mode`, → `bank_name`, `description`). Snake_case on the Python
  boundary; map to the engine's expected keys in one place (`constants.py`).
- Never hand-edit generated JDM JSON; regenerate it via `scripts/generate_jdm.py`.

## Tooling configuration (define in `pyproject.toml` / config files)

- **Ruff** — linter + import sorting. Enable at least `E,F,I,UP,B,SIM,ASYNC`; line
  length 100. Ruff is the single source of lint truth.
- **Black** — formatter, line length 100, kept consistent with Ruff.
- **Mypy** — `strict = true` for `src/app`; tests may relax. CI fails on type errors.
- **Pytest** — `rootdir` at repo root; `pythonpath = ["src"]`; `asyncio_mode = "auto"`;
  test discovery under `tests/`. Coverage gate ≥ 80% on changed services (don't block
  the whole monorepo on one team).
- **pre-commit** — run ruff, black, mypy, end-of-file/trailing-whitespace fixers, and a
  Conventional-Commits commit-msg check. Every contributor installs it.

## Testing conventions

- Mirror the source layout: `tests/services/<service>/{unit,integration}/`.
- Unit tests isolate a single module (parser, validator, builder, evaluator); integration
  tests exercise the router via `httpx.AsyncClient` against the app.
- Each service provides fixtures in its own `conftest.py`; shared fixtures (app, client,
  db session) live in the top-level `tests/conftest.py`.
- Tests must not depend on production data files — use trimmed fixtures
  (`fixtures/sample_matrix.xlsx`, `fixtures/applicants.json`).

## Docker & Compose rules

- One **multi-stage** `docker/api/Dockerfile`: a `base` stage (deps), a `dev` stage
  (dev deps + reload), a `prod` stage (slim, non-root user, Gunicorn + Uvicorn workers).
- `compose.yaml` is the base stack; `compose.dev.yaml` adds bind-mounts/hot-reload/debug
  ports; `compose.prod.yaml` removes mounts, sets worker counts, adds healthchecks.
  Always combine base + one override (`-f compose.yaml -f compose.dev.yaml`).
- Containers run as a non-root user in prod. Secrets come from env/secret managers,
  never baked into images.

## Adding a new service (keep the repo conflict-free)

Follow `docs/service_template.md`. In short: create
`src/app/services/<new>/` with the standard files, expose a module-level `router` and a
prefixed `Settings`, add `requirements/services/<new>.in`, create
`migrations/versions/<new>/`, add a `tests/services/<new>/` tree, and add a CODEOWNERS
line. Because of auto-discovery you should **not** need to edit any shared file to
register the service — if you think you do, that's a design smell to raise.

## When unsure

If a requested change would violate an invariant above (cross-service import, a central
registry file, an unprefixed global setting, a cross-service migration), pause and
explain the conflict with the modular-monolith design before proceeding. Surfacing it is
preferred over silently coupling the services.
