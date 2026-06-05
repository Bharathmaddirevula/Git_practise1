---
title: Environment & Tooling
tags: [debtfactory, environment, docker, windows]
created: 2026-06-03
updated: 2026-06-03
---

# 🐳 Environment & Tooling (Docker-first)

There is **no local Python or venv**. Every command runs inside the same dev
image, so the whole team + CI use identical Python (3.12) and dependency versions.
You only need **Docker Desktop** and **git**. See [[Docker & Data Stores]] and
[[Troubleshooting Log]].

## The one image

- `docker/api/Dockerfile` → `base` (runtime deps) → `dev` (adds ruff/black/mypy/
  pytest + bind-mounted source) / `prod` (slim, non-root, gunicorn).
- Deps install from `requirements/*.in` at build time (no committed lockfiles).
  Constraint files can't have extras, so the build strips them:
  `sed 's/\[[^]]*\]//g' base.in > base.txt`.
- `PYTHONPATH=/app/src` is set in the image — no editable install needed.

## Daily commands

Windows → `.\dev.ps1 <cmd>` · Mac/Linux/WSL → `make <cmd>`:

| cmd | what |
| --- | ---- |
| `up` | build + start api, db, redis, adminer (hot reload) |
| `test` | `pytest -q` in a container |
| `lint` | ruff + black --check + mypy |
| `check` | lint + types + tests (**what CI runs**) |
| `migrate` | apply SQL migrations |
| `shell` | bash into the dev image |

Raw equivalent: `docker compose -f compose.yaml -f compose.dev.yaml run --rm --no-deps api <cmd>`.

## Why Docker-first

- **No "works on my machine"** — CI builds the same image and runs the same
  commands, so green locally ⇒ green in CI.
- New devs are productive in one command (`up`) — no Python install, no venv, no
  dependency drift.

## Windows gotchas (still relevant)

- **`make` isn't on Windows by default** → use `.\dev.ps1` (same verbs).
- PowerShell wraps a native exe's **stderr** as a red `NativeCommandError` even on
  success — check for the real success line, not the red text.
- The migration runner connects to **`db:5432`** inside the container (compose
  network), not `localhost:5433` (that host port is for tools like Adminer/psql).

## Optional: local venv for IDE autocomplete only

Not required to build/run/test. If your editor wants an interpreter, create a
throwaway 3.12 venv for IntelliSense — but **run all gates via Docker**. (A leftover
`.venv` greenlet `.pyd` can stay locked by the editor's language server; it's
git-ignored and harmless.)

#environment #docker #windows
