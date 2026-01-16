#!/usr/bin/env bash
set -euo pipefail

# Entrypoint for the elinity backend image.
# Responsibilities:
# - Materialize Firebase credentials if provided via environment variables
# - Start uvicorn with the PORT provided by the environment (default 8080)

# If FIREBASE_JSON_BASE64 is provided, decode it to /app/keys/firebase.json
if [ -n "${FIREBASE_JSON_BASE64:-}" ]; then
	mkdir -p /app/keys
	echo "$FIREBASE_JSON_BASE64" | base64 -d > /app/keys/firebase.json
	echo "[entrypoint] Wrote /app/keys/firebase.json from FIREBASE_JSON_BASE64"
fi

# If FIREBASE_JSON is provided as plain JSON content, write that too
if [ -n "${FIREBASE_JSON:-}" ]; then
	mkdir -p /app/keys
	printf "%s" "$FIREBASE_JSON" > /app/keys/firebase.json
	echo "[entrypoint] Wrote /app/keys/firebase.json from FIREBASE_JSON"
fi

# Default PORT (can be provided by Azure App Service at runtime)
: ${PORT:=8081}

echo "[entrypoint] Starting uvicorn on 0.0.0.0:${PORT} (SKIP_HEAVY_IMPORTS=${SKIP_HEAVY_IMPORTS:-})"

# Exec into uvicorn so signals are forwarded correctly
exec uvicorn main:app --host 0.0.0.0 --port "$PORT"