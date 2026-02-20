# ============================================================
# SOVEREIGN_START.ps1 — The "God Script" for Realms 2 Riches
# ============================================================
# USAGE: .\SOVEREIGN_START.ps1 [-Prune] [-Yolo]

param (
    [switch]$Prune,
    [switch]$Yolo
)

$ErrorActionPreference = "Stop"

# --- BRANDING ---
Write-Host ""
Write-Host "  REALMS  2  RICHES" -ForegroundColor Green
Write-Host "  SOVEREIGN INTELLIGENCE NETWORK" -ForegroundColor Green
Write-Host "  v3.0.0-PLATINUM | SYSTEM: INITIALIZING" -ForegroundColor Gray
Write-Host ""

# --- 1. DOCKER CHECK & CLEAN ---
Write-Host "[1/6] Verifying Container Runtime..." -ForegroundColor Cyan

if (-not (Get-Process "Docker Desktop" -ErrorAction SilentlyContinue)) {
    Write-Host "⚠️  Docker Desktop not running. Starting..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Start-Sleep -Seconds 15
}

if ($Prune) {
    if ($Yolo -or (Read-Host "⚠️  NUCLEAR OPTION: Prune all Docker data? (y/n)") -eq 'y') {
        Write-Host "🔥 Pruning System..." -ForegroundColor Red
        docker system prune -af --volumes
    }
}

# --- 2. BUILD & LAUNCH ---
Write-Host "[2/6] Orchestrating Infrastructure..." -ForegroundColor Cyan
docker-compose -f infra/docker/docker-compose.prod.yml down --remove-orphans 2>$null
docker-compose -f infra/docker/docker-compose.prod.yml up -d --build

# --- 3. HEARTBEAT DETECTION ---
Write-Host "[3/6] Establishing Neural Link..." -ForegroundColor Cyan
$maxRetries = 30
$retry = 0
$healthy = $false

while ($retry -lt $maxRetries) {
    try {
        $res = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -ErrorAction Stop
        if ($res.status -eq "ok") {
            $healthy = $true
            Write-Host "✅ Neural Link Established." -ForegroundColor Green
            Write-Host "   Agents Online: $($res.agents)" -ForegroundColor Gray
            Write-Host "   RAG Memory:    $($res.rag_docs) Vectors" -ForegroundColor Gray
            break
        }
    } catch {
        Write-Host "   ...waiting for pulse ($($retry+1)/$maxRetries)..." -ForegroundColor DarkGray
        Start-Sleep -Seconds 2
        $retry++
    }
}

if (-not $healthy) {
    Write-Host "❌ FATAL: Neural Link Failed." -ForegroundColor Red
    docker logs docker-orchestrator-api-1 --tail 50
    exit 1
}

# --- 4. SEEDING & LEARNING START ---
Write-Host "[4/6] Seeding Product Catalog..." -ForegroundColor Cyan
docker exec docker-orchestrator-api-1 python -m orchestrator.src.core.catalog.ingest

Write-Host "[5/6] Activating Learning Stream..." -ForegroundColor Cyan
# Trigger the background autonomous loop explicitly if needed, or rely on internal scheduler
# We just verify the log exists
$logs = docker logs docker-orchestrator-api-1 --tail 100
if ($logs -match "AUTONOMOUS AGENT") {
    Write-Host "✅ Learning Loop Active." -ForegroundColor Green
} else {
    Write-Host "⚠️  Learning Loop initializing in background..." -ForegroundColor Yellow
}

# --- 6. CLI READY ---
Write-Host "[6/6] System Ready." -ForegroundColor Green
Write-Host ""
Write-Host "Command Center:"
Write-Host "  > r2r status" -ForegroundColor White
Write-Host "  > r2r shell" -ForegroundColor White
Write-Host ""
Write-Host "Frontend: http://localhost:5173 (Local) or Vercel URL" -ForegroundColor Gray
