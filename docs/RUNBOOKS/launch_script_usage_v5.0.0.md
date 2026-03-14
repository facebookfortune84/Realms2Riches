# Master Launch Script Usage v5.0.0

This document provides instructions for using the Realms2Riches Master Launch Script.

## Overview
The `ops/scripts/launch.ps1` script is the primary entry point for deploying and verifying the Realms2Riches production environment. It automates the entire lifecycle: **BUILD -> TEST -> DEPLOY -> VERIFY**.

## Usage
Run the script from the root of the repository using PowerShell.

```powershell
.\ops\scripts\launch.ps1
```

## Lifecycle Phases

### 1. Git Preparation
- Checks for a clean working tree.
- Automatically commits pending changes with a system timestamp.
- Pulls the latest changes from the `main` branch.

### 2. Versioning & Integrity
- Reads the current version from the `VERSION` file.
- Executes `scripts/hash_registry.py` to ensure file integrity.

### 3. Dual-Core Synchronization
- Runs `infra/scripts/sync_cores.py` to synchronize the primary and secondary cores.

### 4. Build & Testing
- Executes unit and integration tests.
- Runs the live E2E verification suite (`tests/e2e/test_live_frontend.py`).

### 5. Deployment & Orchestration
- (In Production) Rebuilds and launches the Sovereign Swarm containers via `docker-compose`.
- Performs health checks on all active cells.

### 6. Final Diagnostics
- Executes `scripts/readiness_proofs.py` to verify the 25 points of readiness.

## Verification
The script is designed to be idempotent and safe. If any phase fails, the script will abort immediately and log the failure.
