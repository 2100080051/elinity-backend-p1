#!/usr/bin/env bash
# Create a service key on P1 by calling POST /auth/create_service_key
# Requires: ADMIN_JWT env var (the admin's JWT). Optional: KEY_NAME, P1_BASE_URL
# Writes `secret_service_key.txt` in repo root (WARNING included) — move to your secrets store.

set -euo pipefail

P1_BASE_URL=${P1_BASE_URL:-http://localhost:8000}

if [ -z "${ADMIN_JWT-}" ]; then
  echo "ERROR: ADMIN_JWT is not set. Export the admin user's JWT and re-run." >&2
  exit 2
fi

NAME_PARAM=""
if [ -n "${KEY_NAME-}" ]; then
  NAME_PARAM="?name=$(printf '%s' "$KEY_NAME" | jq -s -R -r @uri)"
fi

echo "Creating service key at ${P1_BASE_URL}/auth/create_service_key"
resp=$(curl -s -w "%{http_code}" -X POST "${P1_BASE_URL}/auth/create_service_key${NAME_PARAM}" -H "Authorization: Bearer ${ADMIN_JWT}" -H "Content-Type: application/json")
http_code=${resp: -3}
body=${resp%???}

if [ "$http_code" != "200" ] && [ "$http_code" != "201" ]; then
  echo "ERROR: create_service_key failed (HTTP $http_code):" >&2
  echo "$body" >&2
  exit 3
fi

plain_key=$(echo "$body" | jq -r '.api_key // empty')
key_id=$(echo "$body" | jq -r '.id // empty')

if [ -z "$plain_key" ]; then
  echo "ERROR: response did not contain api_key:" >&2
  echo "$body" >&2
  exit 4
fi

cat > secret_service_key.txt <<EOF
# WARNING: This file contains a plain-text service API key.
# Move this value into a secure secret store (e.g., Azure Key Vault, AWS Secrets Manager,
# HashiCorp Vault) and delete this file from the repository.
# Key id: ${key_id}
${plain_key}
EOF

echo "Service key created (id: ${key_id}). Plain key written to secret_service_key.txt"
echo "Remove that file and store the key in a secure secret manager." 
