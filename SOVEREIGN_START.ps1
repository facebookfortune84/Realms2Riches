# ============================================================
# SOVEREIGN_START.ps1 - Grand Orchestrator Launch (v6.0.0)
# ============================================================
param (
    [switch]$FullPrune,
    [switch]$SkipTests,
    [switch]$PushToOrigin
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:ENV_MODE = "prod"

# Production URLs
$BackendUrl = "https://glowfly-sizeable-lazaro.ngrok-free.dev"
$FrontendUrl = "https://frontend-two-xi-gal9lkptfi.vercel.app/"

Write-Host "`n  R E A L M S   2   R I C H E S" -ForegroundColor Magenta -BackgroundColor Black
Write-Host "  S O V E R E I G N   M A T R I X" -ForegroundColor Green -BackgroundColor Black
Write-Host "  v6.0.0-FINAL | INDUSTRIAL DOMINANCE SEQUENCE`n" -ForegroundColor Gray

# --- -1. ORPHANED PROCESS CLEANUP ---
Write-Host "[*] Purging conflicting processes..." -ForegroundColor Gray
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    $proc = Get-Process -Id $port8000.OwningProcess -ErrorAction SilentlyContinue
    if ($proc.ProcessName -eq "python" -or $proc.ProcessName -eq "uvicorn") {
        Write-Host "  -> Terminating Port 8000 conflict (PID $($proc.Id))..." -ForegroundColor Yellow
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
}

# --- 0. SOURCE CONTROL SECURED ---
Write-Host "[0/9] Securing Lineage..." -ForegroundColor Cyan
git add .
$status = git status --porcelain
if ($status) {
    $ts = Get-Date -Format "yyyyMMdd-HHmm"
    git commit -m "Vanguard Release Pulse: $ts"
    Write-Host "  -> Local state secured." -ForegroundColor Gray
}

if ($PushToOrigin) {
    Write-Host "  -> Syncing with Origin (dev)..." -ForegroundColor Yellow
    git push origin dev
}

# --- 1. INDUSTRIAL TESTING ---
if (-not $SkipTests) {
    Write-Host "[1/9] Initiating Sovereign Deep Audit (Industrial Protocol)..." -ForegroundColor Magenta
    python scripts/matrix_deep_audit.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ CRITICAL: Deep Audit Failed. System state is DEGRADED. Deployment Aborted." -ForegroundColor Red
        exit 1
    }
}

# --- 2. DOCKER PURGE & REBUILD ---
Write-Host "[2/9] Refreshing Infrastructure..." -ForegroundColor Cyan
if ($FullPrune) {
    Write-Host "  -> Executing Total System Prune (Mandatory cleanup requested)..." -ForegroundColor Red
    docker system prune -af --volumes
} else {
    Write-Host "  -> Pruning existing containers..." -ForegroundColor Yellow
    docker-compose -f infra/docker/docker-compose.prod.yml down -v
}

Write-Host "  -> Building and Starting Container Stack..." -ForegroundColor Cyan
docker-compose -f infra/docker/docker-compose.prod.yml up -d --build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ CRITICAL: Docker Stack failed to initialize." -ForegroundColor Red
    exit 1
}

# --- 3. GATEWAY INITIALIZATION ---
Write-Host "[3/9] Establishing Neural Uplink (Ngrok)..." -ForegroundColor Cyan
$ngrokProc = Get-Process -Name "ngrok" -ErrorAction SilentlyContinue
if (-not $ngrokProc) {
    # Extract domain from .env.prod
    $domainLine = Get-Content .env.prod | Select-String "BACKEND_URL="
    $domain = ($domainLine.ToString().Split("=")[1].Trim() -replace "https://", "" -replace "http://", "")
    Write-Host "  -> Launching tunnel for $domain" -ForegroundColor Gray
    Start-Process ngrok -ArgumentList "http --domain=$domain 8000" -NoNewWindow
    Start-Sleep -Seconds 5
} else {
    Write-Host "  -> Tunnel active." -ForegroundColor Green
}

# --- 4. VANGUARD HEALTH CHECK ---
Write-Host "[4/9] Probing Matrix Pulse..." -ForegroundColor Cyan
$healthy = $false
$retry = 0
while ($retry -lt 20 -and -not $healthy) {
    try {
        $res = Invoke-RestMethod -Uri "$BackendUrl/health" -Method Get -Headers @{"ngrok-skip-browser-warning"="true"} -ErrorAction SilentlyContinue
        if ($res.status -eq "SOVEREIGN") {
            $healthy = $true
            Write-Host "`n  -> API online and SOVEREIGN." -ForegroundColor Green
        }
    } catch {
        Write-Host "." -NoNewline -ForegroundColor DarkGray
    }
    $retry++
    Start-Sleep -Seconds 2
}

if (-not $healthy) {
    Write-Host "`n❌ CRITICAL: API Heartbeat not detected at $BackendUrl" -ForegroundColor Red
    exit 1
}

# --- 5. HYPER-AUTOMATION ENGAGEMENT ---
Write-Host "[5/9] Initializing Autonomous Revenue Loops..." -ForegroundColor Magenta
# Start Outreach, Trend-Jacking, Inbox Monitoring, and Watchdog
Start-Process python -ArgumentList "scripts/continuous_outreach_daemon.py" -NoNewWindow
Start-Process python -ArgumentList "scripts/trend_jacking_daemon.py" -NoNewWindow
Start-Process python -ArgumentList "scripts/inbox_closer_daemon.py" -NoNewWindow
Start-Process python -ArgumentList "scripts/vanguard_watchdog.py" -NoNewWindow
Write-Host "  -> Hyper-Automation Suite: ACTIVE (Outreach, Content, Closing, Watchdog)." -ForegroundColor Gray

# --- 6. FRONTEND DEPLOYMENT ---
Write-Host "[6/9] Syncing Static Assets to Statis..." -ForegroundColor Cyan
if ($PushToOrigin) {
    Write-Host "  -> Merging dev into statis for production sync..." -ForegroundColor Yellow
    git checkout statis
    git merge dev --no-ff -m "Production Release: $(Get-Date)"
    git push origin statis
    git checkout dev
}

# --- 7. FINAL REPORT ---
Write-Host "`n=================================================" -ForegroundColor Gray
Write-Host "💎 SOVEREIGN MATRIX IS LIVE 💎" -ForegroundColor Green
Write-Host "  - UI:      $FrontendUrl"
Write-Host "  - CORE:    $BackendUrl"
Write-Host "  - LOGS:    docker-compose -f infra/docker/docker-compose.prod.yml logs -f"
Write-Host "=================================================" -ForegroundColor Gray
Write-Host "`nThe money is moving. System locked." -ForegroundColor Cyan
