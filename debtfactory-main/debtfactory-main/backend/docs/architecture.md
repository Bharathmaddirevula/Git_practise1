# Architecture — Feature-Sliced Modular Monolith

## Why this shape

One deployable FastAPI application, internally split into **four self-contained
feature services**. We get the operational simplicity of a monolith (one image,
one database, one deploy) with much of the team-autonomy of microservices: each
sub-team owns a vertical slice and ships in parallel **without** fighting over
shared files.

The design optimizes for one thing above all: **minimal merge conflicts** for a
multi-team codebase.

## The slices

```
src/app/
├── main.py            # app factory; mounts health + auto-discovered routers
├── api/               # router auto-discovery, health/readiness
├── core/              # shared infra: config, db, logging, errors, middleware
├── common/            # shared contracts (schemas) + utils — the ONLY sharing path
└── services/
    ├── rule_engine/   # zen-engine eligibility decisioning  (PRIMARY)
    ├── auth/          # multi-channel authentication
    ├── domain_logs/   # live log streaming (SSE/WS)
    └── ocr_jobs/      # async OCR (Celery + Redis)
```

Each service owns its `router`, `schemas`, `models`, `service`, `dependencies`,
`exceptions`, `constants`, and `config`.

## Dependency rule (one-way)

```
services/<x>  ──►  app.core      (allowed)
services/<x>  ──►  app.common    (allowed)
services/<x>  ──►  services/<y>  (FORBIDDEN)
```

A service never imports another service. Cross-service needs go through a
published contract in `common/` or an asynchronous event/queue — never a direct
import. This is what lets two teams edit two folders simultaneously without
coupling.

## Convention over central registration

The merge-conflict hotspot in most monoliths is the file *everyone* edits to
"register" their thing. We remove those entirely:

| Concern    | How it's wired                                                       |
| ---------- | -------------------------------------------------------------------- |
| Routers    | `api/router_registry.py` scans `services/*/router.py` for `router`.  |
| Settings   | `core/settings_registry.py` composes each `services/*/config.py`.    |
| Migrations | Alembic **branch labels**, one `migrations/versions/<service>/` dir. |
| Deps       | Per-service `requirements/services/<service>.in` fragments.          |
| Ownership  | `.github/CODEOWNERS` maps each slice to its team.                    |

Adding a service touches **zero** shared files.

## Request lifecycle

```
client → middleware (request-id, timing)
       → router (HTTP only)
       → service (orchestration + business rules)
       → engine/repos/channels (per-service internals)
       → typed exception? → central handler → standard JSON envelope
```

## Layered responsibilities (within a service)

- `router.py` — HTTP only (paths, status codes, request/response models).
- `service.py` — orchestration + business rules; framework-agnostic.
- `schemas.py` — Pydantic v2 DTOs (never expose ORM models).
- `models.py` — SQLAlchemy ORM only.
- `dependencies.py` — FastAPI `Depends` providers.
- `exceptions.py` — typed errors subclassing `core.exceptions.AppException`.

See [`adr/0001-modular-monolith.md`](adr/0001-modular-monolith.md) for the
decision record and [`service_template.md`](service_template.md) for how to add a
new slice.
