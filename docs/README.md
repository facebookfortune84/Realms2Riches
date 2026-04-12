# Docs index (navigation for humans & agents)

| Document | Use when |
|----------|-----------|
| [PATH_FORWARD.md](PATH_FORWARD.md) | Planning the next execution slice; aligning PRD ↔ Taskmaster ↔ code |
| [SWARM_DIRECTOR_PLAYBOOK.md](SWARM_DIRECTOR_PLAYBOOK.md) | You want to direct agents without becoming the full-time implementer |
| [ARCHITECTURE.md](ARCHITECTURE.md) | High-level system narrative (points to deeper maps below) |
| [architecture/api-endpoints.md](architecture/api-endpoints.md) | Verifying HTTP/WebSocket routes |
| [architecture/services-and-interactions.md](architecture/services-and-interactions.md) | Understanding processes (API, worker, DB, Redis, MCP) |
| [architecture/feature-map.md](architecture/feature-map.md) | Finding files for a business feature |
| [architecture/REPO_CLEANUP.md](architecture/REPO_CLEANUP.md) | Dealing with duplicate trees and generated artifacts |
| [LAUNCH_SEQUENCE.md](LAUNCH_SEQUENCE.md) | Ordered checklist from repo hygiene through production cutover |
| [DRIFT_PREVENTION.md](DRIFT_PREVENTION.md) | Secrets policy, branch conventions, and single sources of truth |

Operational runbooks live under [RUNBOOKS/](RUNBOOKS/). Product PRDs under [.taskmaster/docs/products/](../.taskmaster/docs/products/), [.taskmaster/docs/PRD-launch-monetization-v1.md](../.taskmaster/docs/PRD-launch-monetization-v1.md), and [.taskmaster/docs/prd.txt](../.taskmaster/docs/prd.txt).
