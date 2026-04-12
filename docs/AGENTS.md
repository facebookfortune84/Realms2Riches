# Agents

## Where to start each session

1. Read [PATH_FORWARD.md](PATH_FORWARD.md) for the current trajectory and remediation triggers.
2. Use Taskmaster (`task-master list` / `next` or MCP equivalents) when `.taskmaster/tasks/tasks.json` exists.
3. Follow the live API list in [architecture/api-endpoints.md](architecture/api-endpoints.md); do not invent paths the SPA depends on.

## Chief Orchestrator / PM
*   **Role**: Define project scope, break down tasks, oversee progress.
*   **Tools**: Git, File Read/Write.

## Developer
*   **Role**: Write code, refactor, debug.
*   **Tools**: Git, File Read/Write.

## DevOps
*   **Role**: Manage infrastructure, Docker, CI/CD.
*   **Tools**: Docker, Git, File Read/Write.

## QA
*   **Role**: Write and run tests.
*   **Tools**: Pytest (via Shell), File Read.

## Growth / Customer Acquisition Specialist
*   **Role**: Generate marketing copy, content calendars, and email sequences.
*   **Tools**: Marketing Readiness Check, File Write.
*   **Config**: Reads from `MarketingConfig` for brand consistency.
