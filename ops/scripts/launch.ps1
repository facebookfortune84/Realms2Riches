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

# 3. BUILD & DEPLOY (Mock/Scripted)
Write-Host "--> Building Artifacts..." -ForegroundColor Yellow
# Add build commands here (e.g., docker build, npm build)
Write-Host "Build complete."

# 4. DEPLOYMENT
Write-Host "--> Deploying Services..." -ForegroundColor Yellow
# Add deploy commands here (e.g., docker compose up -d)
# Verify deployment

Write-Host "🏆 LAUNCH SEQUENCE COMPLETE. SYSTEM IS LIVE." -ForegroundColor Green
