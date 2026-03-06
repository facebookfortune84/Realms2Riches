# ============================================================
# SOVEREIGN_START.ps1 - Vanguard Launch Commander (v5.5.0)
# ============================================================
param (
    [switch]$Prune,
    [switch]$ForceRelease,
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."

# --- -1. CLEANUP ORPHANED PROCESSES ---
Write-Host "Cleaning up orphaned API processes..." -ForegroundColor Gray
Get-Process -Name "uvicorn", "python" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -eq "" } | Stop-Process -Force -ErrorAction SilentlyContinue
# Specific port cleanup
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    Write-Host "  -> Killing process on port 8000..." -ForegroundColor Yellow
    Stop-Process -Id $port8000.OwningProcess -Force -ErrorAction SilentlyContinue
}

Write-Host "`n  R E A L M S   2   R I C H E S" -ForegroundColor Magenta
Write-Host "  S O V E R E I G N   M A T R I X" -ForegroundColor Green
Write-Host "  v5.5.0-VANGUARD | INDUSTRIAL LAUNCH SEQUENCE`n" -ForegroundColor DarkGray

# --- 0. PRE-FLIGHT GOVERNANCE ---
Write-Host "[0/8] Securing Development Lineage..." -ForegroundColor Cyan
git add .
$status = git status --porcelain
if ($status) {
    $ts = Get-Date -Format "yyyyMMdd-HHmm"
    git commit -m "Vanguard Pulse: $ts [Auto-Secure before Launch]"
    Write-Host "  -> Snapshot secured in 'dev' branch." -ForegroundColor Gray
}

# --- 1. CORE SYNCHRONIZATION ---
Write-Host "[1/8] Synchronizing Secondary Core..." -ForegroundColor Cyan
if (Test-Path "core_secondary") {
    Write-Host "  -> Aligning secondary assets with primary..." -ForegroundColor Gray
    # Selective sync of docs and logic
    Copy-Item -Path "core_secondary/orchestrator/src" -Destination "orchestrator/" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  -> Core Alignment Complete." -ForegroundColor Green
}

# --- 2. SYSTEM INTEGRITY AUDIT ---
if (-not $SkipTests) {
    Write-Host "[2/8] Executing 106-Pass Coverage Engine..." -ForegroundColor Magenta
    python scripts/matrix_coverage_engine.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ CRITICAL: Coverage Scan Failed. Launch Aborted." -ForegroundColor Red
        exit 1
    }

    Write-Host "`n[3/8] Verifying Swarm Integrity..." -ForegroundColor Magenta
    python scripts/test_system_integrity.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ CRITICAL: Integrity Test Failed." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[2-3/8] Skipping Verification (NOT RECOMMENDED)." -ForegroundColor Yellow
}

# --- 4. DOCKER INFRASTRUCTURE ---
Write-Host "[4/8] Starting High-Density Persistence (Postgres)..." -ForegroundColor Cyan
if ($Prune) {
    docker-compose -f infra/docker/docker-compose.prod.yml down -v
}
docker-compose -f infra/docker/docker-compose.prod.yml up -d postgres
Write-Host "  -> Database Container Active." -ForegroundColor Green

# --- 5. API COMMAND CENTER ---
Write-Host "[5/8] Launching Sovereign API..." -ForegroundColor Cyan
$apiProcess = Start-Process uvicorn -ArgumentList "orchestrator.src.core.api:app --host 0.0.0.0 --port 8000" -NoNewWindow -PassThru
Write-Host "  -> API Server PID: $($apiProcess.Id)" -ForegroundColor Gray

# Wait for API to be healthy
Write-Host "  -> Waiting for API heartbeat..." -ForegroundColor Gray
$maxRetries = 10
$retryCount = 0
$healthy = $false
while ($retryCount -lt $maxRetries -and -not $healthy) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -ErrorAction SilentlyContinue
        if ($response.status -eq "healthy") {
            $healthy = $true
            Write-Host "  -> API is ONLINE." -ForegroundColor Green
        }
    } catch {
        $retryCount++
        Start-Sleep -Seconds 2
    }
}

if (-not $healthy) {
    Write-Host "❌ CRITICAL: API failed to start in time." -ForegroundColor Red
    exit 1
}

# --- 6. TUNNELING & CONNECTIVITY ---
Write-Host "[6/8] Opening Global Gateway (Ngrok)..." -ForegroundColor Cyan
$ngrokPath = if (Get-Command ngrok -ErrorAction SilentlyContinue) { "ngrok" } elseif (Test-Path "infra/tools/ngrok/ngrok.exe") { "./infra/tools/ngrok/ngrok.exe" } else { $null }

if ($ngrokPath) {
    # Check if ngrok is already running
    $existingNgrok = Get-Process -Name "ngrok" -ErrorAction SilentlyContinue
    if ($existingNgrok) {
        Write-Host "  -> Ngrok is already running. Skipping startup." -ForegroundColor Yellow
    } else {
        # Extract domain from .env.prod if possible
        $backendUrlLine = Get-Content .env.prod | Select-String "BACKEND_URL="
        if ($backendUrlLine) {
            $backendUrl = $backendUrlLine.ToString().Split("=")[1].Trim()
            if ($backendUrl -like "*ngrok-free.dev*") {
                $domain = $backendUrl -replace "https://", "" -replace "http://", ""
                Write-Host "  -> Using custom domain: $domain" -ForegroundColor Gray
                Start-Process $ngrokPath -ArgumentList "http --domain=$domain 8000" -NoNewWindow
            } else {
                Start-Process $ngrokPath -ArgumentList "http 8000" -NoNewWindow
            }
            Write-Host "  -> Public Gateway Activated." -ForegroundColor Green
        }
    }
} else {
    Write-Host "  -> WARNING: Ngrok not found. Webhooks will be local-only." -ForegroundColor Yellow
}

# --- 7. REVENUE RECONCILIATION ---
Write-Host "[7/8] Running Revenue Loop Validation..." -ForegroundColor Magenta
python scripts/verify_revenue_loop.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "  -> WARNING: Revenue loop returned non-zero. Check Stripe connectivity." -ForegroundColor Yellow
}

# --- 8. FULL SWARM ACTIVATION ---
Write-Host "[8/8] UNLEASHING THE SWARM (Conscious Blitz)..." -ForegroundColor Green
# Start the conscious monetization cycle in a new window to keep it active
Start-Process python -ArgumentList "scripts/conscious_monetization.py"

if ($ForceRelease) {
    Write-Host "`n[RELEASE] Pushing verified state to STASIS branch..." -ForegroundColor Yellow
    git checkout stasis
    git merge dev --no-ff -m "Automated Vanguard Release Merge"
    git checkout dev
}

Write-Host "`n💎 SOVEREIGN MATRIX IS FULLY OPERATIONAL 💎" -ForegroundColor Green
Write-Host "==============================================="
Write-Host "  API URL:    http://localhost:8000"
Write-Host "  TRANSPARENCY: http://localhost:8000/api/v1/swarm/transparency"
Write-Host "  LOGS:       tail -f data/logs/swarm_activity.log"
Write-Host "==============================================="
Write-Host "`nWatch the money move. Launch sequence complete." -ForegroundColor Cyan
