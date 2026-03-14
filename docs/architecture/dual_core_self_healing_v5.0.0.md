# Dual-Core Redundancy & Self-Healing v5.0.0

This document describes the high-availability and self-healing architecture of Realms2Riches.

## Dual-Core Redundancy
Realms2Riches employs a **Dual-Core Architecture**, ensuring that a secondary, fallback core (`core_secondary/`) is always available to maintain operations.

### Core Synchronization
The primary and secondary cores are synchronized via the `infra/scripts/sync_cores.py` script. 
- **Source**: `orchestrator/src`
- **Target**: `core_secondary/orchestrator/src`
- **Synced Directories**: `agents`, `core`, `logging`, `memory`, `tools`, `validation`.

## Autonomous Self-Healing
The `SelfHealingService` (`orchestrator/src/core/self_healing.py`) provides an automated mechanism to detect and repair environmental or structural failures.

### Healing Triggers
- **System Startup**: Baseline healing is performed during the `Orchestrator` startup.
- **Task Failure**: Any exception caught during the `submit_task_stream` process triggers an immediate healing cycle.
- **Backlog Tasks**: The `AutonomousBacklog` proactively identifies missing assets and generates maintenance tasks.

### Repairs Performed
- **Directory Restoration**: Ensures all 8 critical data directories exist.
- **Asset Recovery**: Restores the baseline `sovereign_strategy_guide_v3.txt` if missing.
- **Schema Validation**: Checks and repairs the application database schema.
- **RAG Integrity**: Verifies the vector store state.
- **Environment Checks**: Confirms `.env.prod` is present and correctly configured.

## Verification
Automated verification of self-healing can be performed using:
- `tests/agent_scenarios/test_self_healing_core.py`
