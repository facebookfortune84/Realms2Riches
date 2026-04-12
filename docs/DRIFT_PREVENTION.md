# Drift prevention and project alignment

## Single sources of truth

| Area | Source of truth |
|------|------------------|
| API surface | `docs/architecture/api-endpoints.md` and `orchestrator/src/core/api.py` |
| Frontend → backend wiring | `frontend/src/lib/apiBase.js`, `frontend/vite.config.js` |
| Monetization behavior | `orchestrator/src/core/monetization/` + Stripe dashboard |
| Operator workflow | `docs/SWARM_DIRECTOR_PLAYBOOK.md`, `docs/PATH_FORWARD.md` |
| Executable backlog | `.taskmaster/tasks/tasks.json` (file storage; see `.taskmaster/config.json`) |

## Secrets and compliance

- **Never** commit `.cursor/mcp.json`. It is listed in `.gitignore`. Use `.cursor/mcp.json.example` for structure only.
- If any production key was ever committed or pasted into tooling, **rotate** it in the provider console before launch.
- Treat `data/customers/leads.json` and `data/marketing/leads.json` as **PII**: keep them out of version control (see `.gitignore`).

## Lineage and generated noise

- `data/lineage/contribution_*.json` files are local snapshots; they are ignored by git. Regenerate or archive intentionally if you need them for audits.
- Do not commit `orchestrator.db` or `test-results/`.

## Branch policy (suggested)

| Branch | Role |
|--------|------|
| `main` | Release-ready, protected, CI green |
| `dev` | Integration branch for day-to-day merges |
| `stasis` | Stabilization / freeze before promoting to `main` |
| `release/x.y.z` | Optional short-lived branch for hotfixes or tagged releases |

Promote in order: feature → `dev` → `stasis` → `main`. Avoid force-pushing `main`.

## Task hygiene

- After changing scope, run `task-master validate-dependencies` (or fix manually in `tasks.json`) so the graph stays acyclic.
- Prefer updating task **details** with decisions (provider choice, URL scheme) so agents do not re-litigate settled questions.
