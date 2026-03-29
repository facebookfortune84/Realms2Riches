# Realms2Riches Release Manager
param (
    [string]$VersionTag
)

$ErrorActionPreference = "Stop"

if (-not $VersionTag) {
    Write-Host "Usage: .\publish_release.ps1 -VersionTag v5.X.X" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 INITIATING RELEASE SEQUENCE: $VersionTag" -ForegroundColor Cyan

# 1. Check Status
$status = git status --porcelain
if ($status) {
    Write-Host "❌ Working directory unclean. Commit changes to 'dev' first." -ForegroundColor Red
    exit 1
}

# 2. Verify Branch
$branch = git branch --show-current
if ($branch.Trim() -ne "dev") {
    Write-Host "❌ Must be on 'dev' branch to release." -ForegroundColor Red
    exit 1
}

try {
    # 3. Tag Dev
    Write-Host "Step 1: Tagging Dev..." -ForegroundColor Gray
    git tag -a $VersionTag -m "Release $VersionTag"
    
    # 4. Merge to Stasis
    Write-Host "Step 2: Merging to Stasis..." -ForegroundColor Gray
    git checkout stasis
    git merge dev
    
    # 5. Return to Dev
    Write-Host "Step 3: Returning to Dev..." -ForegroundColor Gray
    git checkout dev
    
    Write-Host "✅ RELEASE COMPLETE." -ForegroundColor Green
    Write-Host "   - Tag: $VersionTag applied"
    Write-Host "   - Stasis: Updated"
    Write-Host "   - Dev: Active"
} catch {
    Write-Host "❌ RELEASE FAILED: $_" -ForegroundColor Red
    git checkout dev 2>$null
    exit 1
}
