# ============================================================
# SOVEREIGN_LAUNCH_V2.ps1 - Unified Deployment Script
# ============================================================
param (
    [switch]$Production,
    [switch]$BuildOnly
)

$ENV_FILE = if ($Production) { ".env.prod" } else { ".env" }
Write-Host "🚀 Launching Realms2Riches Sovereign Stack ($ENV_FILE)..." -ForegroundColor Cyan

# 1. Environment Verification
if (!(Test-Path $ENV_FILE)) {
    Write-Host "❌ ERROR: $ENV_FILE not found. Initialization failed." -ForegroundColor Red
    exit
}

# 2. Docker Orchestration
Write-Host "🐳 Building/Starting Docker Containers..." -ForegroundColor Yellow
docker-compose -f infra/docker/docker-compose.yml --env-file $ENV_FILE down --remove-orphans
if ($BuildOnly) {
    docker-compose -f infra/docker/docker-compose.yml --env-file $ENV_FILE build
    exit
}
docker-compose -f infra/docker/docker-compose.yml --env-file $ENV_FILE up -d

# 3. Connectivity Verification
Write-Host "📡 Verifying Backend Connectivity..." -ForegroundColor Gray
Start-Sleep -Seconds 5
$Health = curl.exe -s http://localhost:8000/health
if ($Health -match "ok") {
    Write-Host "✅ Backend is ONLINE." -ForegroundColor Green
} else {
    Write-Host "⚠️  Backend check failed. Check logs in infra/docker." -ForegroundColor Red
}

Write-Host "🏆 SYSTEM IS LIVE. MISSION: LAMBORGHINI RUN." -ForegroundColor Green
