# Prelaunch Verification Script for Realms2Riches
# Usage: .\ops\scripts\prelaunch.ps1
# This script is DETERMINISTIC and TRUTHFUL.

$ErrorActionPreference = "Stop"

Write-Host "🚀 STARTING PRELAUNCH VERIFICATION..." -ForegroundColor Cyan

# 1. Check for Python
if (Test-Path "venv\Scripts\python.exe") {
    $PYTHON_CMD = "venv\Scripts\python.exe"
} elseif (Get-Command "python" -ErrorAction SilentlyContinue) {
    $PYTHON_CMD = "python"
} else {
    Write-Error "Python not found. Please install Python."
    exit 1
}

Write-Host "Using Python: $PYTHON_CMD" -ForegroundColor Gray

# 2. Start Backend (Local Mode)
Write-Host "--> Starting Backend (Local Mode)..." -ForegroundColor Yellow
$backendProcess = Start-Process $PYTHON_CMD -ArgumentList "scripts/run_server.py" -PassThru -NoNewWindow
$backendUrl = "http://127.0.0.1:8000"
$maxRetries = 30
$retryCount = 0
$serverUp = $false

try {
    while ($retryCount -lt $maxRetries) {
        try {
            $response = Invoke-WebRequest -Uri "$backendUrl/health" -Method Get -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Backend is ONLINE at $backendUrl" -ForegroundColor Green
                $serverUp = $true
                break
            }
        } catch {
            Start-Sleep -Seconds 2
            $retryCount++
            Write-Host "Waiting for backend... ($retryCount/$maxRetries)"
        }
    }

    if (-not $serverUp) {
        Write-Error "❌ Backend failed to start within timeout."
        exit 1
    }

    # 3. Run Test Matrix
    Write-Host "--> Running Test Matrix..." -ForegroundColor Yellow
    
    # Define critical suites
    $testSuites = @(
        @{ Name="Unit Tests"; Command="pytest tests/unit" },
        @{ Name="E2E Tests"; Command="pytest tests/e2e" },
        @{ Name="Integration Tests"; Command="pytest tests/integration" },
        @{ Name="Core Secondary E2E"; Command="pytest core_secondary/tests/e2e" }
    )

    $failedSuites = @()

    foreach ($suite in $testSuites) {
        Write-Host "Running $($suite.Name)..."
        # We use python -m pytest to be safe
        $cmd = $suite.Command -replace "pytest", "$PYTHON_CMD -m pytest"
        Invoke-Expression $cmd
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "$($suite.Name) FAILED (Exit Code: $LASTEXITCODE)" -ForegroundColor Red
            $failedSuites += $suite.Name
        } else {
            Write-Host "✅ $($suite.Name) PASSED" -ForegroundColor Green
        }
    }

    if ($failedSuites.Count -gt 0) {
        Write-Host "❌ PRELAUNCH FAILED. The following suites failed:" -ForegroundColor Red
        foreach ($s in $failedSuites) { Write-Host " - $s" -ForegroundColor Red }
        exit 1
    } else {
        Write-Host "🏆 ALL PRELAUNCH CHECKS PASSED." -ForegroundColor Green
    }

} finally {
    # Cleanup
    if ($backendProcess) {
        Write-Host "Stopping Backend..."
        Stop-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue
    }
}
