# ============================================================
# SOVEREIGN DEPLOY - Auto-Commit & Push
# ============================================================
param (
    [string]$Message = "feat: automated sovereign update"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 INITIATING DEPLOYMENT SEQUENCE..." -ForegroundColor Cyan

# 1. Run Tests (Fast Fail)
# Write-Host "🧪 Running Tests..." -ForegroundColor Yellow
# npm test --prefix infra/cli
# if ($LASTEXITCODE -ne 0) { Write-Error "Tests Failed. Aborting."; exit 1 }

# 2. Add & Commit
Write-Host "💾 Committing Changes..." -ForegroundColor Yellow
git add .
git commit -m "$Message"

# 3. Push
Write-Host "☁️  Pushing to Remote..." -ForegroundColor Yellow
git push

Write-Host "✅ DEPLOYMENT SUCCESSFUL." -ForegroundColor Green
Write-Host "   Triggers: Vercel (Frontend), Docker Build (Backend)" -ForegroundColor Gray
