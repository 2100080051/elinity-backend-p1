# Build and run the Docker image locally and run the smoke test.
param(
    [string]$ImageName = "elinity-backend:local",
    [int]$Port = 8080
)

Write-Host "Building image $ImageName..."
docker build -t $ImageName .

Write-Host "Starting container on port $Port..."
$cid = docker run -d -p ${Port}:8080 $ImageName
Write-Host "Container id: $cid"

try {
    Write-Host "Waiting for /health to become ready..."
    $start = Get-Date
    while ($true) {
        try {
            $res = Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:$Port/health" -TimeoutSec 5
            if ($res.StatusCode -eq 200) { Write-Host "/health OK:" $res.Content; break }
        } catch {}
        if ((Get-Date) - $start -gt [TimeSpan]::FromSeconds(60)) { throw "Timed out waiting for /health" }
        Start-Sleep -Seconds 1
    }
    Write-Host "Smoke test passed. Press Enter to stop container and exit."
    Read-Host
} finally {
    Write-Host "Stopping and removing container $cid"
    docker stop $cid | Out-Null
    docker rm $cid | Out-Null
}
