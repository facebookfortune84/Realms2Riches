# Sovereign Matrix - Vanguard Launch Guide (v4.0)

## Overview
The `SOVEREIGN_START.ps1` script is the unyielding, ironclad entry point for the Realms2Riches Autonomous Matrix. It guarantees that the entire containerized architecture is built, validated, tested, and secured before any live traffic or API calls are authorized.

## The 7-Step Vanguard Sequence

### [0/7] Git Pulse & Remote Lineage
The script automatically stages all changes and creates an atomic `sov-pulse-{timestamp}` commit. It generates a git tag and attempts to push these tags to the remote repository. This ensures that every launch has an exact, recoverable snapshot in the cloud.

### [1/7] Docker Validation
Validates that the Docker daemon is running on the host OS. Includes a `--Prune` flag to execute a nuclear wipe of all previous images, containers, and volumes to guarantee a 100% clean build state.

### [2/7] Forging Infrastructure
Executes `docker-compose up --build -d` using the production configuration, standing up the Orchestrator, PostgreSQL, Vector Store, and background worker nodes.

### [3/7] Neural Heartbeat
Actively polls the `/health` endpoint of the API up to 200 times. It validates the connection to the database and confirms that the AI agents have securely connected to their knowledge bases.

### [4/7] Universal Matrix Diagnostics (NEW)
**The most critical addition.** The script invokes `tests/matrix_runner.py` directly on the host using Poetry. 
*   This script dynamically scans the `tests/matrix/` directory for any file matching `test_*.py`.
*   It executes them using `pytest`.
*   It caches the cryptographic hash of passing files to `tests/.matrix_index.json`. It will only re-test files that have been modified or that failed previously, saving massive amounts of time on boot.
*   **If a single test fails, the boot sequence halts. The swarm will not fly if there is a crack in the hull.**

### [5/7] Master Roundup Audit
Runs the internal `final_roundup_audit.py` script inside the container to verify internal states, environment variables, and memory allocations.

### [6/7] Seeding & Learning
Ingests the newly scraped Stripe catalogs into the Vector Store so the agents are immediately aware of the new pricing and links. It also runs the `backfeed_awareness.py` loop so the Swarm knows its current operational capacity.

### [7/7] Matrix Live
Provides the command center endpoints for the Frontend and Backend.

## Execution
To launch normally:
```powershell
.\SOVEREIGN_START.ps1
```

To execute a clean slate build (will ask for confirmation):
```powershell
.\SOVEREIGN_START.ps1 -Prune
```

To bypass the confirmation prompt (YOLO MODE):
```powershell
.\SOVEREIGN_START.ps1 -Prune -Yolo
```