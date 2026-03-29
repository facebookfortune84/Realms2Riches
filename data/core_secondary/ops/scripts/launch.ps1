# Master Launch Script for Realms2Riches
# Usage: .\ops\scripts\launch.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 INITIATING MASTER LAUNCH SEQUENCE..." -ForegroundColor Cyan

# 1. GIT SANITY CHECK
Write-Host "Checking Git Status..."
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Warning "Working directory is not clean. Committing changes..."
    # git add .
    # git commit -m "Pre-launch auto-commit"
}

# 2. RUN PRELAUNCH VERIFICATION
Write-Host "--> Executing Prelaunch Verification..." -ForegroundColor Yellow
try {
    .\ops\scripts\prelaunch.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ PRELAUNCH FAILED. Aborting Launch."
        exit 1
    }
} catch {
    Write-Error "❌ PRELAUNCH SCRIPT CRASHED. Aborting Launch."
    exit 1
}

# 3. BUILD ARTIFACTS
Write-Host "--> Building Docker Images..." -ForegroundColor Yellow
docker compose -f infra/docker/docker-compose.prod.yml build
if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Docker Build Failed."
    exit 1
}
Write-Host "✅ Build complete."

# 4. DEPLOYMENT
Write-Host "--> Deploying Sovereign Stack..." -ForegroundColor Yellow
docker compose -f infra/docker/docker-compose.prod.yml up -d
if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Docker Compose Up Failed."
    exit 1
}

# 5. VERIFY LIVE STATUS
Write-Host "--> Verifying Production Endpoints..." -ForegroundColor Yellow
$prodUrl = "https://api.realms2riches.com"
# In a real setup, we might wait for the ngrok URL to be reachable
$maxRetries = 15
$retryCount = 0
$live = $false

while ($retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "$prodUrl/health" -Method Get -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $live = $true
            break
        }
    } catch {
        Write-Host "Waiting for production API... ($($retryCount+1)/$maxRetries)"
        Start-Sleep -Seconds 5
        $retryCount++
    }
}

if (-not $live) {
    Write-Error "❌ Production API failed to start."
    exit 1
}

Write-Host "🏆 LAUNCH SEQUENCE COMPLETE. SYSTEM IS LIVE." -ForegroundColor Green
Write-Host "Backend: https://api.realms2riches.com" -ForegroundColor Gray
Write-Host "Frontend: https://realms2riches.com" -ForegroundColor Gray
Write-Host "Transparency: https://api.realms2riches.com/api/v1/swarm/transparency" -ForegroundColor Gray

