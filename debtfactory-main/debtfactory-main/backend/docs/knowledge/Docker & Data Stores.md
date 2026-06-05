---
title: Docker & Data Stores
tags: [debtfactory, docker, postgres, redis, ports]
created: 2026-06-03
---

# 🐳 Docker & Data Stores

Postgres + Redis run in Docker; the host venv connects to them for [[Database Migrations|migrations]] and local runs.

## Host-port map (checked 2026-06-03)

Before assigning ports, check what's busy:

```powershell
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Get-NetTCPConnection -State Listen | ? { $_.LocalPort -in 5432,6379,8000 } | Select LocalPort,OwningProcess
```

| Host port | Status | Used by |
| --------- | ------ | ------- |
| 5432 | ❌ busy | a native Postgres (not ours) |
| 8000 | ❌ busy | another local process |
| 8080 | ❌ busy | another local process |
| **5433** | ✅ free | → mapped to docker Postgres |
| **6379** | ✅ free | → mapped to docker Redis |

> Many old containers from other projects exist but are **Exited** — exited containers don't hold host ports.

## Compose layout

- `compose.yaml` — base (api, **db**, **redis**); internal network uses service names (`db:5432`, `redis:6379`).
- `compose.dev.yaml` — dev override; **publishes** `db → 5433:5432`, `redis → 6379:6379`, and the **Adminer** DB UI on `8081 → 8080`.

## Browse the DB in a browser (Adminer)

Clicking a Postgres port (5433) in Docker Desktop just shows a browser error —
Postgres speaks its own wire protocol, not HTTP. Use **Adminer** instead:

> In Docker Desktop → container `loan-platform-adminer-1` → **click the `8081` port**
> (or open <http://localhost:8081>). Log in:

| Field | Value |
| ----- | ----- |
| System | PostgreSQL |
| Server | `db` (pre-filled via `ADMINER_DEFAULT_SERVER`) |
| Username | `loan` |
| Password | `loan` |
| Database | `loan_platform` |

Server is **`db`** (the compose service name on the internal network), *not*
`localhost` — Adminer runs inside Docker and reaches Postgres by service name.

## Commands

```powershell
# bring up only the data stores
docker compose -f compose.yaml -f compose.dev.yaml up -d db redis
# health / ping
docker inspect --format '{{.State.Health.Status}}' loan-platform-db-1   # -> healthy
docker exec loan-platform-redis-1 redis-cli ping                        # -> PONG
# psql into the db
docker exec -it loan-platform-db-1 psql -U loan -d loan_platform
# tear down (keep data) / wipe data
docker compose -f compose.yaml -f compose.dev.yaml down
docker compose -f compose.yaml -f compose.dev.yaml down -v   # also drops pgdata volume
```

## Connection strings (from the host)

```
DATABASE_URL=postgresql+asyncpg://loan:loan@localhost:5433/loan_platform
OCR_BROKER_URL=redis://localhost:6379/0
```

These live in `.env` (gitignored). Containers themselves use `@db:5432` / `redis:6379` on the compose network.

#docker #postgres #redis #ports
