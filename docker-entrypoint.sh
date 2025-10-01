#!/usr/bin/env bash
set -euo pipefail

echo "==> Container entrypoint starting"

# Wait for optional pre-start delay (useful if DB is coming up elsewhere)
if [ -n "${PRE_START_SLEEP:-}" ]; then
  echo "Pre-start sleep for ${PRE_START_SLEEP}s"
  sleep "${PRE_START_SLEEP}"
fi

if [ "${SKIP_MIGRATIONS:-0}" != "1" ]; then
  echo "==> Running alembic migrations: upgrade head"
  uv run alembic upgrade head
else
  echo "==> SKIP_MIGRATIONS is set, skipping migrations"
fi

if [ "${RUN_INITIAL_DATA:-0}" = "1" ]; then
  echo "==> Running initial data script"
  # run initial data script but don't fail container start on errors
  uv run python -m app.db_init.initial_data || true
fi

echo "==> Entrypoint finished — starting application"

if [ "$#" -gt 0 ]; then
  echo "==> Exec: $@"
  exec "$@"
else
  exec uv run uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
fi
