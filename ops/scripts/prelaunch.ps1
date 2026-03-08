# Realms2Riches - Prelaunch Pipeline v1.1.0
# This script rebuilds containers, starts them, and runs the full test matrix.

$ErrorActionPreference = "Stop"

function Write-Log($message, $color = "White") {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $message" -ForegroundColor $color
}

# 0. GIT STATE
Write-Log "--- PHASE 0: GIT STATE ---" "Cyan"
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Log "Uncommitted changes detected. Committing..." "Yellow"
    git add .
    git commit -m "Pre-launch auto-commit: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Log "✅ Changes committed." "Green"
} else {
    Write-Log "✅ Working tree clean." "Green"
}

# 1. DOCKER ENGINE CHECK
Write-Log "--- PHASE 1: DOCKER CHECK ---" "Cyan"
try {
    docker ps > $null
    Write-Log "✅ Docker engine is responding." "Green"
} catch {
    Write-Log "❌ ERROR: Docker engine is not running. Please start Docker Desktop manually." "Red"
    exit 1
}

# 2. BUILD & RESTART CONTAINERS
Write-Log "--- PHASE 2: CONTAINER REBUILD ---" "Cyan"
Write-Log "Loading environment from .env.prod and rebuilding containers..."
if (Test-Path ".env.prod") {
    # Use --env-file to pass variables to docker-compose
    docker-compose --env-file .env.prod -f infra/docker/docker-compose.yml up -d --build --force-recreate
} else {
    Write-Log "⚠️ WARNING: .env.prod not found. Attempting build without it..." "Yellow"
    docker-compose -f infra/docker/docker-compose.yml up -d --build --force-recreate
}
Write-Log "✅ Containers started." "Green"

# 3. WAIT FOR HEALTH
Write-Log "--- PHASE 3: HEALTH CHECK ---" "Cyan"
$maxRetries = 30
$retryCount = 0
$healthy = $false
$healthUrl = "http://localhost:8000/health"

Write-Log "Waiting for backend health check ($healthUrl)..."
while ($retryCount -lt $maxRetries -and -not $healthy) {
    try {
        $response = Invoke-RestMethod -Uri $healthUrl -Method Get
        if ($response.status -eq "ok") {
            $healthy = $true
            Write-Log "✅ Backend is healthy." "Green"
        }
    } catch {
        $retryCount++
        Start-Sleep -Seconds 2
        Write-Log "  -> Retrying ($retryCount/$maxRetries)..." "Yellow"
    }
}

if (-not $healthy) {
    Write-Log "❌ ERROR: Backend failed to become healthy in time." "Red"
    exit 1
}

# 4. RUN TEST MATRIX
Write-Log "--- PHASE 4: TEST MATRIX ---" "Cyan"
$env:PYTHONPATH = "."
[int]$totalFailures = 0

function Run-Suite($name, $path) {
    Write-Log "Running Suite: $name ($path)..." "Yellow"
    # We use Out-Host to ensure pytest output goes to console but isn't captured by the variable
    pytest $path | Out-Host
    if ($LASTEXITCODE -ne 0) {
        Write-Log "❌ FAILED: $name" "Red"
        return 1
    }
    Write-Log "✅ PASSED: $name" "Green"
    return 0
}

$totalFailures += [int](Run-Suite "Unit Tests" "tests/unit")
$totalFailures += [int](Run-Suite "Agent Capabilities" "tests/agents")
$totalFailures += [int](Run-Suite "Self-Healing Scenarios" "tests/agent_scenarios")
$totalFailures += [int](Run-Suite "E2E Flow" "tests/e2e")

# 5. FINAL VERDICT
Write-Log "--- PHASE 5: FINAL VERDICT ---" "Cyan"
if ($totalFailures -eq 0) {
    Write-Log "💎 PRELAUNCH SUCCESSFUL. SYSTEM IS STABLE." "Green"
    exit 0
} else {
    Write-Log "❌ PRELAUNCH FAILED. $totalFailures suite(s) failed." "Red"
    exit 1
}
