# ============================================================
# SOVEREIGN_START.ps1 - Grand Orchestrator Launch (v11.0.0)
# ============================================================
param (
    [switch]$LocalOnly,
    [switch]$FullPrune,
    [switch]$SkipTests,
    [string]$CommitMsg = "feat: autonomous traffic & core sync [$(Get-Date -Format 'yyyyMMdd-HHmm')]"
)

$ErrorActionPreference = "Continue" # Don't stop the whole script if one process fails
$env:PYTHONPATH = "." 

Write-Host "`n  R E A L M S   2   R I C H E S" -ForegroundColor Magenta -BackgroundColor Black
Write-Host "  S O V E R E I G N   M A T R I X" -ForegroundColor Green -BackgroundColor Black
Write-Host "  v11.0.0 | AUTOMATED REVENUE & TRAFFIC SYSTEM`n" -ForegroundColor Gray

# --- 0. PRE-FLIGHT ---
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found in PATH. Please install Python 3.10+."
    exit 1
}

# --- 1. CORE SYNC ---
Write-Host "[1/8] Syncing Primary -> Secondary Core..." -ForegroundColor Cyan
python scripts/sync_core.py

# --- 2. LINEAGE ---
Write-Host "[2/8] Recording Lineage..." -ForegroundColor Cyan
python scripts/hash_registry.py

# --- 3. DOCKER (DB & REDIS) ---
Write-Host "[3/8] Starting Backend Services (Docker)..." -ForegroundColor Cyan
if ($FullPrune) { docker-compose -f infra/docker/docker-compose.yml down -v }
docker-compose -f infra/docker/docker-compose.yml up -d db redis

# --- 4. START ORCHESTRATOR API ---
Write-Host "[4/8] Igniting Orchestrator API (Port 8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoProfile", "-Command", "python -m uvicorn orchestrator.src.core.api:app --host 0.0.0.0 --port 8000" -WindowStyle Normal

# --- 5. START WORKER ---
Write-Host "[5/8] Waking Swarm Worker..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoProfile", "-Command", "python -m arq orchestrator.src.core.worker.WorkerSettings" -WindowStyle Normal

# --- 6. START OPTIMIZER ---
Write-Host "[6/8] Starting Funnel Optimizer..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoProfile", "-Command", "python scripts/funnel_optimizer_daemon.py" -WindowStyle Normal

# --- 7. START TRAFFIC DRIVER ---
Write-Host "[7/8] Unleashing Autonomous Traffic Driver..." -ForegroundColor Magenta
Start-Process powershell -ArgumentList "-NoProfile", "-Command", "python scripts/autonomous_traffic_driver.py" -WindowStyle Normal

# --- 8. START FRONTEND ---
Write-Host "[8/8] Launching UI..." -ForegroundColor Cyan
if (Test-Path "frontend") {
    Set-Location frontend
    Start-Process powershell -ArgumentList "-NoProfile", "-Command", "npm run dev" -WindowStyle Normal
    Set-Location ..
}

Write-Host "`n=================================================" -ForegroundColor Gray
Write-Host "🚀 ALL SYSTEMS ONLINE & DRIVING TRAFFIC" -ForegroundColor Green
Write-Host "  - Local UI:     http://localhost:5173"
Write-Host "  - API Docs:     http://localhost:8000/docs"
Write-Host "  - Traffic Log:  logs/traffic_driver.log"
Write-Host "=================================================" -ForegroundColor Gray
Write-Host "Note: Background windows have been opened for each process."
Write-Host "If a window closes immediately, check the logs directory.`n"
