# ============================================================
# SOVEREIGN_START.ps1 - Platinum Robust Launcher (v4.0 Matrix Edition)
# ============================================================
param (
    [switch]$Prune,
    [switch]$Yolo
)

$ErrorActionPreference = "Stop"

Write-Host "`n  R E A L M S   2   R I C H E S" -ForegroundColor Magenta
Write-Host "  S O V E R E I G N   M A T R I X" -ForegroundColor Green
Write-Host "  v4.0-VANGUARD | SYSTEM: INITIALIZING`n" -ForegroundColor DarkGray

# --- 0. SOVEREIGN GIT & LINEAGE SYNC ---
Write-Host "[0/7] Synchronizing Git Pulse & Remote Lineage..." -ForegroundColor Cyan
try {
    git add .
    $timestamp = Get-Date -Format "yyyyMMdd-HHmm"
    $tag = "sov-pulse-$timestamp"
    
    # Check if there are changes to commit
    $status = git status --porcelain
    if ($status) {
        git commit -m "Sovereign Swarm Pulse: $timestamp [Automated Lineage Commit]"
        Write-Host "  -> Changes committed." -ForegroundColor Gray
    } else {
        Write-Host "  -> Work tree clean. Proceeding to tag." -ForegroundColor Gray
    }
    
    git tag -a $tag -m "Sovereign Intelligence Network Lifecycle Point: $tag"
    Write-Host "  -> Tagged locally as $tag" -ForegroundColor Gray
    
    # Attempt Remote Push
    try {
        Write-Host "  -> Pushing lineage to remote..." -ForegroundColor Gray
        git push origin main --tags -q
        Write-Host "SUCCESS: Lineage secured in remote repository." -ForegroundColor Green
    } catch {
        Write-Host "WARNING: Remote push failed. Lineage secured locally only." -ForegroundColor Yellow
    }
} catch {
    Write-Host "WARNING: Git Pulse skipped (Not a git repo or no access)." -ForegroundColor Yellow
}

# --- 1. DOCKER VALIDATION ---
Write-Host "`n[1/7] Verifying Docker Desktop..." -ForegroundColor Cyan
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
Write-Host "`n[2/7] Forging Sovereign Infrastructure..." -ForegroundColor Cyan
docker-compose -f infra/docker/docker-compose.prod.yml down --remove-orphans
docker-compose -f infra/docker/docker-compose.prod.yml up -d --build

# --- 3. PULSE CHECK ---
Write-Host "`n[3/7] Detecting Neural Heartbeat..." -ForegroundColor Cyan
$maxRetries = 200
$retry = 0
$healthy = $false

while ($retry -lt $maxRetries) {
    try {
        $res = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 2
        if ($res.status -eq "ok") {
            $healthy = $true
            Write-Host "SUCCESS: Neural Link Established." -ForegroundColor Green
            Write-Host "   Agents: $($res.agents) | RAG: $($res.rag) Vectors ONLINE" -ForegroundColor Cyan
            Write-Host "   Version: $($res.version)" -ForegroundColor DarkGray
            break
        }
    } catch {
        Write-Host "   ...waiting for API ($($retry+1)/$maxRetries)..." -ForegroundColor DarkGray
        Start-Sleep -Seconds 3
        $retry++
    }
}

if (-not $healthy) {
    Write-Host "ERROR: Neural Link Timeout. Dumping Logs:" -ForegroundColor Red
    docker logs docker-orchestrator-api-1 --tail 20
    exit 1
}

# --- 4. UNIVERSAL TEST MATRIX ---
Write-Host "`n[4/7] Engaging Universal Matrix Diagnostics..." -ForegroundColor Magenta
try {
    # Run the matrix directly on the host using Poetry
    poetry run python tests/matrix_runner.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "CRITICAL MATRIX FRACTURE DETECTED." -ForegroundColor Red
        Write-Host "The Swarm cannot launch until all tests pass." -ForegroundColor Red
        exit 1
    }
    Write-Host "SUCCESS: Matrix is perfectly aligned." -ForegroundColor Green
} catch {
    Write-Host "FATAL MATRIX EXECUTION FAILURE." -ForegroundColor Red
    exit 1
}

# --- 5. SYSTEM INTEGRITY VALIDATION ---
Write-Host "`n[5/7] Running MASTER ROUNDUP AUDIT..." -ForegroundColor Cyan
try {
    docker exec docker-orchestrator-api-1 python scripts/final_roundup_audit.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "CRITICAL SYSTEM DEVIATION DETECTED." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "FATAL AUDIT FAILURE." -ForegroundColor Red
    exit 1
}

# --- 6. SEEDING & LEARNING ---
Write-Host "`n[6/7] Synchronizing Catalog & Learning Streams..." -ForegroundColor Cyan
docker exec docker-orchestrator-api-1 python -m orchestrator.src.core.catalog.ingest
Write-Host "SUCCESS: Learning Stream Online." -ForegroundColor Green

try {
    docker exec docker-orchestrator-api-1 python scripts/backfeed_awareness.py
    Write-Host "SUCCESS: Swarm is Self-Aware." -ForegroundColor Green
} catch {
    Write-Host "WARNING: Awareness Protocol skipped." -ForegroundColor Yellow
}

# --- 7. FINAL READY ---
Write-Host "`n[7/7] SOVEREIGN MATRIX IS LIVE." -ForegroundColor Green
Write-Host "`nCommand Center:"
Write-Host "  > r2r shell" -ForegroundColor White
Write-Host "  > r2r status" -ForegroundColor White
Write-Host "  > poetry run python scripts/yolo_mode_monetization.py" -ForegroundColor Yellow
Write-Host "`nAccess URLS:"
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Gray
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Gray
