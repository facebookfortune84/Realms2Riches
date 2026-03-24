# ============================================================
# SOVEREIGN_START.ps1 - Grand Orchestrator Launch & Deployment (v10.0.0)
# ============================================================
param (
    [switch]$LocalOnly,      # Run locally without pushing to remote
    [switch]$FullPrune,      # Clean docker resources before starting
    [switch]$SkipTests,      # Skip pre-flight tests (NOT RECOMMENDED)
    [string]$CommitMsg = "feat: sovereign sync [$(Get-Date -Format 'yyyyMMdd-HHmm')]"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "." 

# --- CONFIGURATION ---
$BackendUrl = "https://api.realms2riches.com"
$FrontendUrl = "https://app.realms2riches.com"
$DevBranch = "dev"
$StasisBranch = "stasis"

Write-Host "`n  R E A L M S   2   R I C H E S" -ForegroundColor Magenta -BackgroundColor Black
Write-Host "  S O V E R E I G N   M A T R I X" -ForegroundColor Green -BackgroundColor Black
Write-Host "  v10.0.0 | FULL PRODUCTION SYNC SYSTEM`n" -ForegroundColor Gray

# --- 1. CORE & ENVIRONMENT SYNC ---
Write-Host "[1/7] Syncing Primary -> Secondary Core..." -ForegroundColor Cyan
try {
    python scripts/sync_core.py
    if ($LASTEXITCODE -ne 0) { throw "Core sync failed." }
} catch {
    Write-Warning "Core sync script failed. Proceeding, but secondary core may be out of date."
}

# --- 2. LOCAL VERIFICATION ---
if (-not $SkipTests) {
    Write-Host "[2/7] Running System Integrity Checks..." -ForegroundColor Cyan
    try {
        python scripts/test_system_integrity.py
        if ($LASTEXITCODE -ne 0) { throw "Integrity checks failed." }
    } catch {
        Write-Error "System integrity compromised. Fix errors before deploying."
        exit 1
    }
}

# --- 3. LINEAGE & TAGGING ---
Write-Host "[3/7] Recording Lineage & Locking State..." -ForegroundColor Cyan
python scripts/hash_registry.py
# Sync lineage to secondary
if (Test-Path "data/lineage/hash_registry.json") {
    if (-not (Test-Path "core_secondary/data/lineage")) { New-Item -ItemType Directory -Path "core_secondary/data/lineage" -Force }
    Copy-Item "data/lineage/hash_registry.json" "core_secondary/data/lineage/hash_registry.json" -Force
}

# --- 4. GIT OPERATIONS (LOCAL -> REMOTE SYNC) ---
if (-not $LocalOnly) {
    Write-Host "[4/7] Syncing Local -> Remote (GitHub)..." -ForegroundColor Magenta
    
    # Check git status
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        Write-Host "  -> Staging changes (including core_secondary)..." -ForegroundColor Gray
        git add .
        
        Write-Host "  -> Committing: $CommitMsg" -ForegroundColor Gray
        git commit -m "$CommitMsg"
    }

    # Push to Dev
    Write-Host "  -> Pushing to $DevBranch..." -ForegroundColor Gray
    git push origin $DevBranch
    
    # Push to Stasis (Triggers CI/CD for VPS Sync)
    Write-Host "  -> Pushing to $StasisBranch (TRIGGERS VPS SYNC)..." -ForegroundColor Yellow
    git checkout $StasisBranch
    git merge $DevBranch
    git push origin $StasisBranch
    git checkout $DevBranch # Return to dev
    
    Write-Host "  -> Remote Sync Triggered. VPS will update via GitHub Actions." -ForegroundColor Green
} else {
    Write-Host "[4/7] Skipping Remote Sync (Local Only Mode)" -ForegroundColor Yellow
}

# --- 5. CORE ORCHESTRATION ---
Write-Host "[5/7] Starting Local Orchestration..." -ForegroundColor Cyan

if ($FullPrune) {
    docker-compose -f infra/docker/docker-compose.yml down -v --remove-orphans
}
docker-compose -f infra/docker/docker-compose.yml up -d db redis adminer

# Start Primary API
Start-Process python -ArgumentList "-m", "arq", "run", "orchestrator.src.core.worker.WorkerSettings" -NoNewWindow
Start-Process uvicorn -ArgumentList "orchestrator.src.core.api:app --host 0.0.0.0 --port 8000 --reload" -NoNewWindow

# --- 6. SECONDARY CORE (FALLBACK) ---
Write-Host "[6/7] Initializing Secondary Core Fallback..." -ForegroundColor Magenta
# We run secondary on a different port (e.g., 8001) for local fallback testing
if (Test-Path "core_secondary") {
    Start-Process uvicorn -ArgumentList "core_secondary.orchestrator.src.core.api:app --host 0.0.0.0 --port 8001" -NoNewWindow
    Write-Host "  -> Secondary Core STANDBY at http://localhost:8001" -ForegroundColor Gray
}

# --- 7. FRONTEND LAUNCH ---
Write-Host "[7/7] Launching Frontend Interface..." -ForegroundColor Cyan
if (Test-Path "frontend") {
    Set-Location frontend
    Start-Process npm -ArgumentList "run", "dev" -NoNewWindow
    Set-Location ..
}

# --- FINAL STATUS ---
Write-Host "`n=================================================" -ForegroundColor Gray
Write-Host "🚀 REALMS2RICHES MATRIX IS SYNCED & LIVE" -ForegroundColor Green
Write-Host "  - Local UI:     http://localhost:5173"
Write-Host "  - Local API:    http://localhost:8000"
Write-Host "  - Secondary:    http://localhost:8001"
if (-not $LocalOnly) {
    Write-Host "  - VPS Sync:     IN PROGRESS (GitHub Actions)"
    Write-Host "  - Production:   $FrontendUrl"
}
Write-Host "=================================================" -ForegroundColor Gray
