# ============================================================
# SOVEREIGN_START.ps1 — Robust, Health‑Checked Startup Script
# ============================================================

Write-Host "🔥 Waking the Beast..." -ForegroundColor Cyan

# ------------------------------------------------------------
# 1. Start Docker Stack
# ------------------------------------------------------------
Write-Host "[1/3] Launching Docker Containers..." -ForegroundColor Yellow
docker compose -f infra/docker/docker-compose.prod.yml up -d --build

# ------------------------------------------------------------
# 2. Wait for Sovereign API to Become Healthy
# ------------------------------------------------------------
Write-Host "[2/3] Waiting for API Heartbeat..." -ForegroundColor Yellow

$maxAttempts = 40   # up to ~80 seconds
$attempt = 0
$apiHealthy = $false

while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            Write-Host "API is healthy ❤️" -ForegroundColor Green
            $apiHealthy = $true
            break
        }
    }
    catch {
        # API not ready yet — keep waiting
    }

    Start-Sleep -Seconds 2
    $attempt++
    Write-Host "  ...waiting ($attempt/$maxAttempts)" -ForegroundColor DarkYellow
}

if (-not $apiHealthy) {
    Write-Host "❌ API did not become healthy in time. Exiting." -ForegroundColor Red
    exit 1
}

Write-Host "🔐 Security: Signature-First Auth Active (DHCP Enabled)" -ForegroundColor Cyan

# ------------------------------------------------------------
# 3. Seed Product Catalog (Now Safe to Run)
# ------------------------------------------------------------
Write-Host "[3/3] Seeding Product Catalog..." -ForegroundColor Yellow
$env:PYTHONPATH = "."
python -m orchestrator.src.core.catalog.ingest

# ------------------------------------------------------------
# 4. Final Output
# ------------------------------------------------------------
Write-Host ""
Write-Host "✅ THE BEAST IS AWAKE" -ForegroundColor Green
Write-Host "Backend:      http://localhost:8000"
Write-Host "Diagnostics:  http://localhost:8000/api/diagnostics"
Write-Host "Chamber:      ws://localhost:8000/ws/chamber"
Write-Host ""
Write-Host "If ngrok still shows 502, run:  ngrok http 8000 --host-header=rewrite" -ForegroundColor Cyan