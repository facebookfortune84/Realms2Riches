# Realms2Riches - Master Launch Script v5.2.3-SOVEREIGN
# This script orchestrates the full CI/CD pipeline: START -> TEST -> LINEAGE -> DEPLOY

$ErrorActionPreference = "Stop"
$VERSION = Get-Content "VERSION"

function Write-Heading($text) {
    Write-Host "`n======================================================================" -ForegroundColor Cyan
    Write-Host ">>> $text" -ForegroundColor Cyan
    Write-Host "======================================================================`n" -ForegroundColor Cyan
}

# 1. GIT PREPARATION
Write-Heading "PHASE 1: GIT PREPARATION"
$status = git status --porcelain
if ($status) {
    Write-Host "⚠️ Warning: Working tree is not clean." -ForegroundColor Yellow
}

# 2. START BACKEND SERVICES
Write-Heading "PHASE 2: STARTING BACKEND SERVICES"

Write-Host "Starting local backend server..." -ForegroundColor Yellow
$BackendProcess = Start-Process python -ArgumentList "scripts/run_server.py" -PassThru -NoNewWindow

# Wait for health check
$maxRetries = 30
$retryCount = 0
$healthy = $false

Write-Host "Waiting for backend health check (http://127.0.0.1:8000/health)..." -ForegroundColor Yellow
while ($retryCount -lt $maxRetries -and -not $healthy) {
    try {
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
        if ($response.status -eq "ok") {
            $healthy = $true
            Write-Host "✅ Backend is healthy." -ForegroundColor Green
        }
    } catch {
        $retryCount++
        Start-Sleep -Seconds 2
        Write-Host "  -> Retrying ($retryCount/$maxRetries)..."
    }
}

if (-not $healthy) {
    Stop-Process -Id $BackendProcess.Id -Force
    throw "Backend failed to start or is unhealthy."
}

# 3. TEST MATRIX EXECUTION
Write-Heading "PHASE 3: TEST MATRIX EXECUTION"

$env:PYTHONPATH = "."

try {
    Write-Host "Running Unit Tests..." -ForegroundColor Yellow
    pytest tests/unit
    if ($LASTEXITCODE -ne 0) { throw "Unit tests failed." }

    Write-Host "Running Agent Intelligence Tests..." -ForegroundColor Yellow
    pytest tests/agents/test_agent_capabilities.py
    if ($LASTEXITCODE -ne 0) { throw "Agent capability tests failed." }

    Write-Host "Running Self-Healing Scenarios..." -ForegroundColor Yellow
    pytest tests/agent_scenarios/test_self_healing_core.py
    if ($LASTEXITCODE -ne 0) { throw "Self-healing tests failed." }

    Write-Host "Running E2E Verification..." -ForegroundColor Yellow
    pytest tests/e2e/test_full_flow.py tests/e2e/test_marketing_ready_flow.py tests/e2e/test_forge_launch_readiness.py
    if ($LASTEXITCODE -ne 0) { throw "E2E tests failed." }

    Write-Host "✅ ALL TESTS PASSED." -ForegroundColor Green
} finally {
    Write-Host "Stopping local backend server..." -ForegroundColor Yellow
    Stop-Process -Id $BackendProcess.Id -Force
}

# 4. FINAL VERDICT
Write-Heading "PHASE 4: FINAL VERDICT"
python scripts/readiness_proofs.py
Write-Host "💎 SYSTEM IS VERIFIED." -ForegroundColor Green -BackgroundColor Black
