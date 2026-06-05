#!/usr/bin/env bash
# Container entrypoint.
#
# When launching the server (uvicorn/gunicorn) we apply DB migrations first.
# For one-off commands (pytest, ruff, bash, ...) we skip straight to the command
# so `docker compose run --rm api pytest` doesn't need a database.
set -euo pipefail

case "${1:-}" in
  uvicorn | gunicorn)
    echo ">> Applying SQL migrations"
    python scripts/migrate_sql.py
    ;;
esac

echo ">> Starting: $*"
exec "$@"
