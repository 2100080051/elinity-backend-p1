#!/usr/bin/env bash
# Apply Alembic migrations (bash)
# Usage: run from repo root where alembic.ini exists. DATABASE_URL env var must be set.
# This script exits non-zero on any failure.

set -euo pipefail

if [ -z "${DATABASE_URL-}" ]; then
  echo "ERROR: DATABASE_URL is not set. Export it and re-run." >&2
  exit 2
fi

echo "Applying Alembic migrations..."
alembic -c alembic.ini upgrade head
echo "Checking current revision..."
alembic -c alembic.ini current

echo "Alembic migrations applied successfully."
