# ADR 0001 — Feature-Sliced Modular Monolith

- **Status:** Accepted
- **Date:** 2026-06-02
- **Deciders:** Platform team + service sub-teams

## Context

We are building a loan platform backend that four sub-teams develop in parallel:
rule engine (eligibility), authentication, live domain logs, and OCR jobs. We
need to ship fast with many concurrent feature branches while keeping operations
simple. The two failure modes we most want to avoid:

1. **Merge-conflict gridlock** — every team editing the same "register your
   router/setting/migration here" files.
2. **Premature microservices** — the network, deploy, and data-consistency tax of
   separate services before we have the scale or org to justify it.

## Decision

Adopt a **feature-sliced modular monolith**: a single FastAPI application whose
code is split into self-contained vertical slices under `app/services/<service>/`,
with three reinforcing rules:

1. **One-way dependencies.** Services may import `app.core` and `app.common`,
   never another service. Cross-service coupling goes through `common/` contracts
   or an event/queue.
2. **Convention over central registration.** Routers, settings, and migrations
   are auto-discovered (`router_registry`, `settings_registry`, Alembic branch
   labels). No file must be edited by every team.
3. **Codified ownership.** `CODEOWNERS` maps each slice to its team; CI uses
   path filters so a team only pays for its own tests.

## Consequences

**Positive**

- Adding/of editing a service touches zero shared files → near-zero structural
  merge conflicts.
- One image, one DB, one deploy → simple operations and local dev.
- Clear extraction seam: a slice can later become a real microservice because it
  already has no inbound service imports.

**Negative / trade-offs**

- Auto-discovery is slightly more "magical" than an explicit include list; it is
  documented in `architecture.md` to compensate.
- The one-way import rule must be enforced in review (and ideally a lint check).
- A shared database means schema discipline matters; we mitigate with per-service
  table prefixes and branch-labeled migrations.

## Alternatives considered

- **Microservices from day one** — rejected: operational/coordination cost is not
  justified at current scale.
- **Classic layered monolith** (controllers/, models/, services/ by *type*) —
  rejected: maximizes cross-team file contention, the exact thing we're avoiding.
