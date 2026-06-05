# Pull Request

## Summary

<!-- What does this change do and why? -->

## Service(s) touched

<!-- Tick the service this PR is scoped to. Prefer one service per PR. -->

- [ ] rule_engine
- [ ] auth
- [ ] domain_logs
- [ ] ocr_jobs
- [ ] core / common / infra

## Architecture checklist (modular monolith)

- [ ] **No cross-service imports** — this code does not import from another
      `app/services/<other>/`. Cross-service needs go through `app/common/` or an event/queue.
- [ ] **No central registration files edited** — routers/settings/migrations are
      auto-discovered; I did not add a hand-maintained "register every X here" list.
- [ ] New env vars use the service's prefix and are documented in `.env.example`.
- [ ] DB migrations were generated under this service's branch label only.
- [ ] Branch is scoped to a single service directory where possible.

## Testing

- [ ] `ruff check . && black --check . && mypy src` pass.
- [ ] `pytest` passes; changed service keeps coverage ≥ 80%.
- [ ] New behavior has tests.

## Conventional Commit

<!-- e.g. feat(rule-engine): add matrix parser -->
