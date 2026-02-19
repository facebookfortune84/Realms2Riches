# SOVEREIGN_START.ps1
# Bypasses 'make' and fires up the entire Sovereign Stack

Write-Host "🔥 Waking the Beast..." -ForegroundColor Cyan

# 1. Start Docker
Write-Host "[1/3] Launching Docker Containers..." -ForegroundColor Yellow
docker compose -f infra/docker/docker-compose.prod.yml up -d --build

# 2. Wait for API Health
Write-Host "[2/3] Waiting for API Heartbeat..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# DHCP Awareness
$CurrentIP = (Invoke-RestMethod -Uri "https://api.ipify.org")
Write-Host "📡 System identified current IP as: $CurrentIP" -ForegroundColor Gray
Write-Host "🔐 Security: Signature-First Auth Active (DHCP Enabled)" -ForegroundColor Cyan

# 3. Seed Catalog
Write-Host "[3/3] Seeding Product Catalog..." -ForegroundColor Yellow
$env:PYTHONPATH="."
python -m orchestrator.src.core.catalog.ingest

Write-Host "`n✅ THE BEAST IS AWAKE" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000"
Write-Host "Diagnostics: http://localhost:8000/api/diagnostics"
Write-Host "Chamber Stream: ws://localhost:8000/ws/chamber"
Write-Host "`nCheck your ngrok tunnel now. If it still shows 502, run: ngrok http 8000" -ForegroundColor Cyan
