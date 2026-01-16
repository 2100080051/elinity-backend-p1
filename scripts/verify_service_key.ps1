#!/usr/bin/env pwsh
<#
Verify a service key by calling GET /internal/users/{ADMIN_USER_ID}.

Requirements:
- Set `P1_API_KEY` env var to the service key value.
- Set `ADMIN_USER_ID` env var to a known user id to test (this can be an admin's id).
- Optionally set `P1_BASE_URL` (default http://localhost:8000).
#>

if (-not $Env:P1_API_KEY) {
    Write-Error "P1_API_KEY is not set. Set the service key in the environment and re-run."
    exit 2
}
if (-not $Env:ADMIN_USER_ID) {
    Write-Error "ADMIN_USER_ID is not set. Provide a known user id to verify the key against."
    exit 2
}

$P1_BASE_URL = $Env:P1_BASE_URL -or 'http://localhost:8000'
$uri = "$P1_BASE_URL/internal/users/$($Env:ADMIN_USER_ID)"

try {
    $resp = Invoke-RestMethod -Method Get -Uri $uri -Headers @{ Authorization = "Bearer $($Env:P1_API_KEY)" } -ErrorAction Stop
    if ($null -eq $resp -or -not $resp.id) {
        Write-Error "Unexpected response schema. Response: $(ConvertTo-Json $resp -Depth 3)"
        exit 3
    }
    Write-Host "Service key verification succeeded. Received user id: $($resp.id)"
    exit 0
}
catch {
    Write-Error "Service key verification failed: $_"
    exit 4
}
