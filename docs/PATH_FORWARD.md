# Path forward (execution spine)

This document ties together **product intent**, **Taskmaster tasks**, **architecture**, and **day-to-day agent workflow** so humans and agents can parse progress and spot drift early.

## North star

Deliver a **reliable, monetizable “company-in-a-box” stack**: FastAPI orchestrator + Redis/ARQ worker + Postgres, React console, Stripe and affiliate flows, and optional MCP tooling—without silent broken links between UI and API.

Canonical implementation lives at repo root: **`orchestrator/`**, **`frontend/`**, **`scripts/`**, **`mcp_internal/`**, **`infra/`**, **`data/`**. Treat **`core_secondary/`** and **`data/core_secondary/`** as historical mirrors unless you explicitly maintain them (see [architecture/REPO_CLEANUP.md](architecture/REPO_CLEANUP.md)).

## Task tracking (Taskmaster)

1. If `.taskmaster/tasks/tasks.json` exists: run `task-master list` (or MCP `get_tasks`) at session start.
2. Use `task-master next` / `next_task` to pick the next dependency-ready item.
3. Log implementation notes with `update_subtask`; mark done with `set_task_status`.
4. When scope pivots, use `update` / `update_task` from the affected task ID forward.

If tasks have **not** been generated yet: parse the PRD (e.g. `.taskmaster/docs/products/PRD-company-in-a-box-v1.md` or `.taskmaster/docs/prd.txt`) into Taskmaster, then expand high-complexity items.

## Architecture references

| Document | Purpose |
|----------|---------|
| [architecture/api-endpoints.md](architecture/api-endpoints.md) | HTTP + WebSocket routes |
| [architecture/services-and-interactions.md](architecture/services-and-interactions.md) | Processes and data flow |
| [architecture/feature-map.md](architecture/feature-map.md) | Features → files |
| [SWARM_DIRECTOR_PLAYBOOK.md](SWARM_DIRECTOR_PLAYBOOK.md) | Operating model for a human director |

## Remediation triggers (when to stop and fix plumbing)

- Any **new `fetch()`** in the frontend must target a **real route** on `orchestrator/src/core/api.py` or be proxied by Vite.
- **Stripe CLI** forward URL must stay aligned with `POST /api/v1/monetization/webhook` (see root `package.json` script `stripe:listen`).
- **WebSocket** tests (`tests/integration/test_voice_flow.py`) assume **`/ws/voice`** on the main app.
- If **duplicate trees** reappear under `data/core_secondary/`, do not edit them for product work—merge or delete per cleanup guide.

## Planned upgrades (same trajectory)

- Harden `/api/tasks` with auth, timeouts, and streaming (SSE) for long agent runs.
- Persist high-ticket offers and leads in Postgres with admin review instead of JSON files.
- Consolidate Stripe webhook logic into one module once `include_router` is chosen deliberately.

## Path changes

When the product direction shifts, update **this file** and the **PRD**, then run Taskmaster `update --from=<id>` so downstream tasks stay consistent. Agents should cite this document when proposing scope changes.
