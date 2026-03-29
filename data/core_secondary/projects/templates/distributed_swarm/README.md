# Distributed Sovereign Swarm

## Overview
This is a standalone, distributed instance of the Sovereign AI Agent Swarm. It contains the core orchestration logic, top-tier agents, and a suite of tools for autonomous operations.

## Structure
- `orchestrator/`: Core logic for agent management and task execution.
- `scripts/`: Operational scripts for starting the swarm and running specialized tasks.
- `data/`: Local storage for logs, memory, and configuration.

## Quick Start
1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure Environment:**
    Create a `.env` file based on `.env.example` and add your API keys (GROQ, etc.).
3.  **Run the Swarm:**
    ```bash
    python scripts/start_swarm.py
    ```

## Included Agents
- **Manager:** High-level task routing and strategy.
- **Developer:** Code generation and system integration.
- **Marketer:** Content creation and outreach.
- **Auditor:** Integrity checks and quality control.

## License
Sovereign Distributed License v1.0
