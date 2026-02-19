# ============================================================
# SOVEREIGN_START.ps1 — Robust, Health‑Checked Startup Script
# ============================================================

$ErrorActionPreference = "Stop"
Write-Host "Waking the Beast..." -ForegroundColor Cyan

# 0. Check Docker Status
Write-Host "[0/4] Verifying Docker Desktop..." -ForegroundColor Yellow
if (-not (Get-Process "Docker Desktop" -ErrorAction SilentlyContinue)) {
    Write-Host "Docker Desktop is not running. Attempting to start..." -ForegroundColor Gray
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Write-Host "Waiting for Docker to initialize..." -ForegroundColor Gray
    $dockerWait = 0
    while (-not (docker info 2>$null) -and $dockerWait -lt 30) {
        Start-Sleep -Seconds 2
        $dockerWait += 2
        Write-Host "  ...still waiting for daemon..." -ForegroundColor DarkYellow
    }
}

if (-not (docker info 2>$null)) {
    Write-Host "FATAL: Docker daemon is unavailable. Please start Docker Desktop manually." -ForegroundColor Red
    exit 1
}

# 1. Cleanup and Build
Write-Host "[1/4] Preparing Docker Stack..." -ForegroundColor Yellow
# Optional: Use --no-cache if you want a guaranteed fresh start every time
# docker compose -f infra/docker/docker-compose.prod.yml build --no-cache
docker compose -f infra/docker/docker-compose.prod.yml up -d --build

# 2. Wait for Sovereign API to Become Healthy
Write-Host "[2/4] Waiting for API Heartbeat..." -ForegroundColor Yellow

$maxAttempts = 40
$attempt = 0
$apiHealthy = $false

while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            Write-Host "API is healthy!" -ForegroundColor Green
            $apiHealthy = $true
            break
        }
    }
    catch {
        # API not ready yet
    }

    Start-Sleep -Seconds 2
    $attempt++
    Write-Host ("  ...waiting ({0}/{1})" -f $attempt, $maxAttempts) -ForegroundColor DarkYellow
}

if (-not $apiHealthy) {
    Write-Host "ERROR: API did not become healthy. Dumping logs..." -ForegroundColor Red
    docker logs docker-orchestrator-api-1 --tail 50
    exit 1
}

# 3. Seed Product Catalog (Inside Container to ensure dependencies/env)
Write-Host "[3/4] Seeding Product Catalog (Containerized)..." -ForegroundColor Yellow
docker exec docker-orchestrator-api-1 python -m orchestrator.src.core.catalog.ingest
if ($LASTEXITCODE -eq 0) {
    Write-Host "Catalog seeded successfully." -ForegroundColor Green
} else {
    Write-Host "Warning: Catalog seeding failed." -ForegroundColor Red
}

# 4. Final Verification
Write-Host "[4/4] Final Verification..." -ForegroundColor Yellow
$diag = Invoke-WebRequest -Uri "http://localhost:8000/api/diagnostics" -UseBasicParsing
Write-Host "Diagnostics: $($diag.Content)" -ForegroundColor Cyan

# Final Output
Write-Host ""
Write-Host "THE BEAST IS AWAKE" -ForegroundColor Green
Write-Host "Backend:      http://localhost:8000"
Write-Host "Diagnostics:  http://localhost:8000/api/diagnostics"
Write-Host "Chamber:      ws://localhost:8000/ws/chamber"
Write-Host ""
Write-Host "If ngrok shows 502, run: ngrok http 8000 --host-header=rewrite" -ForegroundColor Cyan
