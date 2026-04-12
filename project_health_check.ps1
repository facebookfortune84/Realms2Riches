Write-Host "=== REALMS2RICHES PROJECT HEALTH CHECK ===" -ForegroundColor Cyan

$root = "C:\Realms2Riches"

Write-Host "`n[1/12] Skipping corruption scan (disabled)" -ForegroundColor Yellow

# 2. ENVIRONMENT VALIDATION
Write-Host "`n[2/12] Validating environment variables..." -ForegroundColor Yellow
if (Test-Path "$root\.env.master") {
    python "$root\tools\validate_env.py"
} else {
    Write-Host "[WARNING] .env.master not found - skipping env validation." -ForegroundColor Yellow
}

# 3. BACKEND STATIC ANALYSIS
Write-Host "`n[3/12] Running backend static analysis..." -ForegroundColor Yellow
if (Get-Command pylint -ErrorAction SilentlyContinue) {
    pylint "$root\orchestrator\src" --exit-zero
} else {
    Write-Host "[WARNING] pylint not installed - skipping backend lint." -ForegroundColor Yellow
}

# 4. FRONTEND STATIC ANALYSIS
Write-Host "`n[4/12] Running frontend static analysis..." -ForegroundColor Yellow
cd "$root\frontend"
if ((Get-Content package.json) -match '"lint"') {
    npm run lint
} else {
    Write-Host "[WARNING] No lint script found - skipping frontend lint." -ForegroundColor Yellow
}

# 5. DEPENDENCY VALIDATION
Write-Host "`n[5/12] Checking npm dependencies..." -ForegroundColor Yellow
npm ls --depth=1

Write-Host "`nChecking Python dependencies..." -ForegroundColor Yellow
pip check

# 6. BACKEND UNIT TESTS
Write-Host "`n[6/12] Running backend tests..." -ForegroundColor Yellow
if (Test-Path "$root\orchestrator\tests") {
    cd "$root\orchestrator"
    if (Get-Command pytest -ErrorAction SilentlyContinue) {
        pytest --maxfail=1 --disable-warnings
    } else {
        Write-Host "[WARNING] pytest not installed - skipping backend tests." -ForegroundColor Yellow
    }
} else {
    Write-Host "[WARNING] No backend tests directory - skipping backend tests." -ForegroundColor Yellow
}

# 7. FRONTEND UNIT TESTS
Write-Host "`n[7/12] Running frontend tests..." -ForegroundColor Yellow
cd "$root\frontend"
if ((Get-Content package.json) -match '"test"') {
    npm run test
} else {
    Write-Host "[WARNING] No test script found - skipping frontend tests." -ForegroundColor Yellow
}

# 8. FRONTEND BUILD
Write-Host "`n[8/12] Building frontend..." -ForegroundColor Yellow
npm run build

# 9. API CONTRACT TESTS
Write-Host "`n[9/12] Running API contract tests..." -ForegroundColor Yellow
if (Test-Path "$root\tests\api\contract_tests.py") {
    python "$root\tests\api\contract_tests.py"
} else {
    Write-Host "[WARNING] No API contract tests found - skipping." -ForegroundColor Yellow
}

# 10. INTEGRATION TESTS (Playwright)
Write-Host "`n[10/12] Running integration tests..." -ForegroundColor Yellow
if (Test-Path "$root\tests\integration") {
    cd "$root\tests\integration"
    npx playwright test
} else {
    Write-Host "[WARNING] No integration tests directory - skipping." -ForegroundColor Yellow
}

# 11. FEATURE COMPLETENESS SCAN
Write-Host "`n[11/12] Mapping features and checking completeness..." -ForegroundColor Yellow
if (Test-Path "$root\tools\feature_map.py") {
    python "$root\tools\feature_map.py"
} else {
    Write-Host "[WARNING] feature_map.py not found - skipping." -ForegroundColor Yellow
}

# 12. FINAL REPORT
Write-Host "`n[12/12] Generating final report..." -ForegroundColor Yellow
if (Test-Path "$root\tools\final_report.py") {
    python "$root\tools\final_report.py"
} else {
    Write-Host "[WARNING] final_report.py not found - skipping." -ForegroundColor Yellow
}

Write-Host "`n=== HEALTH CHECK COMPLETE ===" -ForegroundColor Green