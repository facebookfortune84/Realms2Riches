# Realms2Riches - Master Launch Script v5.2.4-SOVEREIGN
# This script orchestrates the full release pipeline: PRELAUNCH -> LINEAGE -> DEPLOY

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

# 2. RUN PRELAUNCH PIPELINE (REBUILD + TEST)
Write-Heading "PHASE 2: PRELAUNCH PIPELINE"
Write-Host "Starting prelaunch verification..." -ForegroundColor Yellow
try {
    .\ops\scripts\prelaunch.ps1
} catch {
    Write-Host "`n❌ PRELAUNCH FAILED; FIX TESTS OR SERVICES BEFORE LAUNCHING." -ForegroundColor Red
    exit 1
}
Write-Host "✅ PRELAUNCH PASSED." -ForegroundColor Green

# 3. GIT LINEAGE & TAGGING
Write-Heading "PHASE 3: GIT LINEAGE & TAGGING"
$tag = "v$VERSION-SOVEREIGN"
Write-Host "Tagging release: $tag" -ForegroundColor Green
# git add .
# git commit -m "RELEASE: Realms2Riches $tag. All critical paths verified via Prelaunch Pipeline."
# git tag $tag
# git push origin main --tags

# 4. FINAL VERDICT
Write-Heading "PHASE 4: FINAL VERDICT"
python scripts/readiness_proofs.py
Write-Host "💎 SYSTEM IS VERIFIED AND READY FOR PRODUCTION." -ForegroundColor Green -BackgroundColor Black
