#!/usr/bin/env pwsh
<#
Apply Alembic migrations (PowerShell)

Requirements:
- Run from the repository root where `alembic.ini` is present.
- Ensure `DATABASE_URL` environment variable is set and points to your target DB.
- Run from a host that can reach the DB. Consider taking a DB backup before running.
#>

if (-not $Env:DATABASE_URL) {
    Write-Error "DATABASE_URL is not set. Set it and re-run."
    exit 2
}

try {
    Write-Host "Applying Alembic migrations..."
    alembic -c alembic.ini upgrade head
    if ($LASTEXITCODE -ne 0) { throw "alembic upgrade failed (exit $LASTEXITCODE)" }

    Write-Host "Migration applied. Current revision:"
    alembic -c alembic.ini current
    if ($LASTEXITCODE -ne 0) { throw "alembic current failed (exit $LASTEXITCODE)" }

    Write-Host "Alembic upgrade successful."
    exit 0
}
catch {
    Write-Error "Error applying migrations: $_"
    exit 3
}
