# ============================================================
# SOVEREIGN_START.ps1 - Platinum Robust Launcher
# ============================================================
param (
    [switch]$Prune,
    [switch]$Yolo
)

$ErrorActionPreference = "Stop"

Write-Host "`n  REALMS  2  RICHES" -ForegroundColor Green
Write-Host "  SOVEREIGN INTELLIGENCE NETWORK" -ForegroundColor Green
Write-Host "  v3.0.0-PLATINUM | SYSTEM: INITIALIZING`n" -ForegroundColor Gray

# --- 1. DOCKER VALIDATION ---
Write-Host "[1/6] Verifying Docker Desktop..." -ForegroundColor Cyan
if (-not (Get-Process "Docker Desktop" -ErrorAction SilentlyContinue)) {
    Write-Host "INFO: Starting Docker Desktop..." -ForegroundColor Gray
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Start-Sleep -Seconds 15
}

if ($Prune) {
    $confirm = "y"
    if (-not $Yolo) {
        $confirm = Read-Host "WARNING: NUCLEAR OPTION. Prune all data? (y/n)"
    }
    if ($confirm -eq "y") {
        Write-Host "INFO: Pruning Docker System..." -ForegroundColor Red
        docker system prune -af --volumes
    }
}

# --- 2. BUILD & LAUNCH ---
Write-Host "[2/6] Building Sovereign Infrastructure..." -ForegroundColor Cyan
docker-compose -f infra/docker/docker-compose.prod.yml down --remove-orphans
docker-compose -f infra/docker/docker-compose.prod.yml up -d --build

# --- 3. PULSE CHECK ---
Write-Host "[3/6] Detecting Neural Heartbeat..." -ForegroundColor Cyan
$maxRetries = 20
$retry = 0
$healthy = $false

while ($retry -lt $maxRetries) {
    try {
        $res = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 2
        if ($res.status -eq "ok") {
            $healthy = $true
            Write-Host "SUCCESS: Neural Link Established." -ForegroundColor Green
            Write-Host "   Agents: $($res.agents) | RAG: $($res.rag_docs) Vectors" -ForegroundColor Gray
            break
        }
    } catch {
        Write-Host "   ...waiting for API ($($retry+1)/$maxRetries)..." -ForegroundColor DarkGray
        Start-Sleep -Seconds 3
        $retry++
    }
}

if (-not $healthy) {
    Write-Host "ERROR: Neural Link Timeout. Check container logs." -ForegroundColor Red
    exit 1
}

# --- 4. SEEDING ---
Write-Host "[4/6] Synchronizing Catalog..." -ForegroundColor Cyan
docker exec docker-orchestrator-api-1 python -m orchestrator.src.core.catalog.ingest

# --- 5. LEARNING STREAM ---
Write-Host "[5/6] Activating Autonomous Learning Stream..." -ForegroundColor Cyan
# The Learning Loop is built into the startup of api.py
Write-Host "SUCCESS: Learning Stream Online." -ForegroundColor Green

# --- 6. FINAL READY ---
Write-Host "[6/6] Sovereign Matrix Ready." -ForegroundColor Green
Write-Host "`nCommand Center:"
Write-Host "  > r2r shell" -ForegroundColor White
Write-Host "  > r2r status" -ForegroundColor White
Write-Host "`nAccess URLS:"
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Gray
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Gray
