# Orchestrator Core v5.0.0

This document outlines the architecture and operation of the Realms2Riches Orchestrator Core.

## Entry Points
The central entry point for the system is the `Orchestrator` class located in `orchestrator/src/core/orchestrator.py`.

### Key Methods
- `startup()`: Initializes the high-density agent matrix, loads Oracle personas/SOPs, and launches the autonomous backlog.
- `submit_task_stream(task_description, project_id)`: The primary method for submitting goals to the swarm.

## Hierarchical Routing & Task Decomposition
The Orchestrator uses a keyword-based routing mechanism to assign tasks to the appropriate **Sovereign Cell**.

| Keywords | Target Cell |
|----------|-------------|
| "code", "build", "infra" | **Cybernetic Engineering** |
| "post", "market", "viral", "lander", "funnel" | **Global Market Force** |
| "price", "revenue", "audit", "sale" | **Revenue Systems** |
| Others | **Integrity Shield** |

### Task Workflow
1. **Routing**: The goal is analyzed for keywords and dispatched to a cell.
2. **Ticketing**: A governance ticket is created to track the task.
3. **Execution**: A random agent within the target cell is selected to process the task asynchronously.
4. **Resolution**: The ticket is resolved, and the result is returned to the user or caller.
5. **Self-Healing**: If a task fails, the `SelfHealingService` is automatically triggered.
