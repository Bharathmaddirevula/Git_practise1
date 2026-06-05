# How to Add a New Service

Adding a service should touch **zero shared files** — everything is
auto-discovered. If you find yourself editing a central registry, stop: that's a
design smell to raise (see [architecture.md](architecture.md)).

## Checklist

1. **Create the slice** under `src/app/services/<new>/` with the standard files:

   ```
   src/app/services/<new>/
   ├── __init__.py
   ├── router.py        # expose a module-level `router` (APIRouter)
   ├── schemas.py       # Pydantic v2 DTOs
   ├── models.py        # SQLAlchemy ORM (subclass core.database.Base)
   ├── service.py       # orchestration / business rules
   ├── dependencies.py  # FastAPI Depends providers
   ├── exceptions.py    # subclass core.exceptions.AppException
   ├── constants.py     # SERVICE_NAME, ROUTE_PREFIX, etc.
   └── config.py        # Settings with a unique env prefix (<NEW>_)
   ```

2. **Expose `router`** — a module-level `APIRouter` in `router.py`. The
   `router_registry` mounts it automatically.

3. **Expose `Settings`** — a `pydantic-settings` model in `config.py` with a
   unique `env_prefix` (e.g. `NEW_`). The `settings_registry` composes it.

4. **Add a requirements fragment** — `requirements/services/<new>.in`
   (`-c ../base.txt` at the top), then run `scripts/compile_requirements.sh`.

5. **Create the migration dir** — `migrations/versions/<new>/.gitkeep`, and add
   it to `version_locations` in `alembic.ini`. Generate revisions under your own
   branch label.

6. **Add a test tree** — `tests/services/<new>/{__init__.py,conftest.py,unit/,integration/}`.

7. **Add a CODEOWNERS line** mapping `src/app/services/<new>/` (and its tests +
   migrations) to your team.

8. **Document env vars** in `.env.example` under a `<NEW>_` group.

## Invariants to honor

- No imports from another `services/<other>/`. Use `common/` or an event.
- No central "register every X" file.
- One env prefix per service; validate at the boundary with Pydantic v2.
- Async-first: async handlers, async sessions, `httpx.AsyncClient` outbound.
