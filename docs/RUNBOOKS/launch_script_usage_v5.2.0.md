# Master Launch Script Usage v5.2.0-SOVEREIGN

## 1. Overview
The `ops/scripts/launch.ps1` script is the central orchestrator for the Realms2Riches release pipeline. It ensures that no code is tagged or deployed unless it passes the full Sovereign Test Matrix.

## 2. Prerequisites
- **PowerShell 7+**
- **Python 3.11+** with `pytest` and `playwright` installed.
- **Git** configured with remote access.
- **.env.prod** populated with active keys.

## 3. Execution
Run the script from the project root:
```powershell
.\ops\scripts\launch.ps1
```

## 4. Pipeline Phases
1. **Git Preparation**: Checks for clean state and pulls latest.
2. **Dual-Core Sync**: Synchronizes the fallback core.
3. **Test Matrix**:
   - Unit tests (`tests/unit`)
   - Agent Intelligence (`tests/agents`)
   - Self-Healing Scenarios (`tests/agent_scenarios`)
   - Live Frontend Crawl (`tests/e2e/test_live_frontend.py`)
4. **Git Lineage**: Commits, tags, and pushes (if enabled).
5. **Deployment**: Launches/restarts system containers.
6. **Diagnostics**: Runs final readiness proofs.

## 5. Failure Behavior
The script uses `Stop` on error. If any test or command fails, the pipeline aborts immediately, preventing a broken release from being tagged or deployed.
