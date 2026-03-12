# ============================================================
# SOVEREIGN_START.ps1 - Dominance Launch Commander (v5.8.0)
# ============================================================
param (
    [switch]$Prune,
    [switch]$ForceRelease,
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:ENV_MODE = "prod"

# Production URLs
$BackendUrl = "https://glowfly-sizeable-lazaro.ngrok-free.dev"
$FrontendUrl = "https://frontend-two-xi-gal9lkptfi.vercel.app/"

# --- -1. CLEANUP ORPHANED PROCESSES ---
Write-Host "Cleaning up orphaned processes..." -ForegroundColor Gray
# Only kill python processes that might conflict with docker binding port 8000
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    $proc = Get-Process -Id $port8000.OwningProcess -ErrorAction SilentlyContinue
    if ($proc.ProcessName -eq "python" -or $proc.ProcessName -eq "uvicorn") {
        Write-Host "  -> Killing conflicting process on port 8000 (PID $($proc.Id))..." -ForegroundColor Yellow
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "`n  R E A L M S   2   R I C H E S" -ForegroundColor Magenta
Write-Host "  S O V E R E I G N   M A T R I X" -ForegroundColor Green
Write-Host "  v5.8.0-PRODUCTION | INDUSTRIAL LAUNCH SEQUENCE`n" -ForegroundColor DarkGray

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
    Write-Host "  -> Skipping destructive sync to protect primary core logic." -ForegroundColor Yellow
    Write-Host "  -> Core Alignment Skipped." -ForegroundColor Green
}

# --- 2. SYSTEM INTEGRITY AUDIT ---
if (-not $SkipTests) {
    Write-Host "[2/8] Executing Coverage Engine..." -ForegroundColor Magenta
    # Using local python for tests before container launch to save time
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

# --- 4. DOCKER INFRASTRUCTURE (SMART REBUILD) ---
Write-Host "[4/8] Launching Production Containers..." -ForegroundColor Cyan
if ($Prune) {
    Write-Host "  -> Pruning old volumes..." -ForegroundColor Yellow
    docker-compose -f infra/docker/docker-compose.prod.yml down -v
}

# Smart Rebuild: --build ensures image updates if dependencies changed.
# Docker caching handles "only when necessary" optimization.
Write-Host "  -> Building and Starting Stack (Orchestrator, Worker, Postgres)..." -ForegroundColor Cyan
docker-compose -f infra/docker/docker-compose.prod.yml up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ CRITICAL: Docker Launch Failed." -ForegroundColor Red
    exit 1
}
Write-Host "  -> Container Stack Active." -ForegroundColor Green

# --- 5. CONNECTIVITY (Ngrok) ---
Write-Host "[5/8] Verifying Global Gateway..." -ForegroundColor Cyan
$ngrokPath = if (Get-Command ngrok -ErrorAction SilentlyContinue) { "ngrok" } elseif (Test-Path "infra/tools/ngrok/ngrok.exe") { "./infra/tools/ngrok/ngrok.exe" } else { $null }

if ($ngrokPath) {
    $existingNgrok = Get-Process -Name "ngrok" -ErrorAction SilentlyContinue
    if (-not $existingNgrok) {
        # Extract domain from .env.prod
        $backendUrlLine = Get-Content .env.prod | Select-String "BACKEND_URL="
        if ($backendUrlLine) {
            $backendUrlVal = $backendUrlLine.ToString().Split("=")[1].Trim()
            if ($backendUrlVal -like "*ngrok-free.dev*") {
                $domain = $backendUrlVal -replace "https://", "" -replace "http://", ""
                Write-Host "  -> Launching Ngrok for domain: $domain" -ForegroundColor Gray
                Start-Process $ngrokPath -ArgumentList "http --domain=$domain 8000" -NoNewWindow
                Start-Sleep -Seconds 3
            } else {
                Start-Process $ngrokPath -ArgumentList "http 8000" -NoNewWindow
            }
        }
    } else {
        Write-Host "  -> Ngrok is already running." -ForegroundColor Yellow
    }
} else {
    Write-Host "  -> WARNING: Ngrok not found. Production URL verification may fail." -ForegroundColor Yellow
}

# --- 6. HEALTH CHECK ---
Write-Host "[6/8] Waiting for API Heartbeat..." -ForegroundColor Cyan
$maxRetries = 60 # Increased timeout for slow tunnel propagation
$retryCount = 0
$healthy = $false
$healthUrl = "$BackendUrl/health"
$localHealthUrl = "http://localhost:8000/health"

Write-Host "  -> Probing Production URL: $healthUrl" -ForegroundColor Gray

while ($retryCount -lt $maxRetries -and -not $healthy) {
    try {
        # First try the production URL
        $response = Invoke-RestMethod -Uri $healthUrl -Method Get -TimeoutSec 5 -Headers @{"ngrok-skip-browser-warning"="true"} -ErrorAction SilentlyContinue
        if ($response.status -eq "SOVEREIGN") {
            $healthy = $true
            Write-Host "`n  -> API is ONLINE and SOVEREIGN at $BackendUrl" -ForegroundColor Green
        } else {
            # Fallback check to local port to ensure container is actually up
            $localResponse = Invoke-RestMethod -Uri $localHealthUrl -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($localResponse.status -eq "SOVEREIGN") {
                Write-Host "L" -NoNewline -ForegroundColor Yellow # L for Local Up
            } else {
                Write-Host "." -NoNewline -ForegroundColor DarkGray
            }
        }
    } catch {
        Write-Host "x" -NoNewline -ForegroundColor Red
    }
    $retryCount++
    Start-Sleep -Seconds 3
}

if (-not $healthy) {
    Write-Host "`n❌ CRITICAL: API failed to start or is unreachable at $healthUrl." -ForegroundColor Red
    Write-Host "  -> Check Docker logs: docker-compose -f infra/docker/docker-compose.prod.yml logs" -ForegroundColor Gray
    exit 1
}

# --- 7. REVENUE RECONCILIATION ---
Write-Host "`n[7/8] Running Revenue Loop Validation..." -ForegroundColor Magenta
python scripts/verify_revenue_loop.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "  -> WARNING: Revenue loop returned non-zero. Check Stripe connectivity." -ForegroundColor Yellow
}

# --- 8. FULL SWARM ACTIVATION ---
Write-Host "[8/8] UNLEASHING THE SWARM (Conscious Blitz)..." -ForegroundColor Green
# Execute the monetization script against the live container
Start-Process python -ArgumentList "scripts/conscious_monetization.py"

if ($ForceRelease) {
    Write-Host "`n[RELEASE] Pushing verified state to STASIS branch..." -ForegroundColor Yellow
    git checkout stasis
    git merge dev --no-ff -m "Automated Vanguard Release Merge"
    git checkout dev
}

Write-Host "`n💎 SOVEREIGN MATRIX IS FULLY OPERATIONAL 💎" -ForegroundColor Green
Write-Host "==============================================="
Write-Host "  API URL:      $BackendUrl"
Write-Host "  FRONTEND URL: $FrontendUrl"
Write-Host "  PROFIT BOARD: python scripts/profit_dashboard.py"
Write-Host "  TRANSPARENCY: $BackendUrl/api/v1/swarm/transparency"
Write-Host "  LOGS:         docker-compose -f infra/docker/docker-compose.prod.yml logs -f"
Write-Host "==============================================="
Write-Host "`nWatch the money move. Launch sequence complete." -ForegroundColor Cyan
