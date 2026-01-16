#!/usr/bin/env pwsh
<#
Create a service key by calling POST /auth/create_service_key on P1.

Requirements:
- Run from the repository root where `alembic.ini` and the app exist.
- Set `ADMIN_JWT` env var to an admin user's JWT.
- Optional: set `KEY_NAME` and `P1_BASE_URL` (default http://localhost:8000).

This script writes `secret_service_key.txt` containing the plain key with a big warning. Move
the key to a secrets manager and delete the file.
#>

if (-not $Env:ADMIN_JWT) {
    Write-Error "ADMIN_JWT is not set. Provide an admin JWT and re-run."
    exit 2
}

$P1_BASE_URL = $Env:P1_BASE_URL -or 'http://localhost:8000'
$nameQuery = ''
if ($Env:KEY_NAME) { $nameQuery = "?name=$( [uri]::EscapeDataString($Env:KEY_NAME) )" }

try {
    Write-Host "Creating service key at $P1_BASE_URL/auth/create_service_key$nameQuery"
    $resp = Invoke-RestMethod -Method Post -Uri "$P1_BASE_URL/auth/create_service_key$nameQuery" -Headers @{ Authorization = "Bearer $($Env:ADMIN_JWT)" } -ErrorAction Stop
}
catch {
    Write-Error "Error calling create_service_key: $_"
    exit 3
}

$plain_key = $resp.api_key
$key_id = $resp.id
if (-not $plain_key) {
    Write-Error "Response did not contain api_key: $(ConvertTo-Json $resp -Depth 3)"
    exit 4
}

$out = @()
$out += "# WARNING: This file contains a plain-text service API key."
$out += "# Move this value into a secure secret store (e.g., Azure Key Vault, AWS Secrets Manager, HashiCorp Vault) and delete this file from the repository."
$out += "# Key id: $key_id"
$out += $plain_key

Set-Content -Path secret_service_key.txt -Value $out -Encoding UTF8

Write-Host "Service key created (id: $key_id). Plain key written to secret_service_key.txt"
Write-Host "Move the key to a secrets store and delete secret_service_key.txt from this repo."
exit 0
