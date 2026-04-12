# Repository cleanup and duplicate trees

## Canonical code paths

Use **only** these for product development:

| Area | Path |
|------|------|
| Backend API & agents | `orchestrator/` |
| Marketing SPA | `frontend/` |
| Automation | `scripts/` |
| MCP | `mcp_internal/` |
| Containers | `infra/docker/` |
| Runtime data | `data/` (except duplicate mirrors below) |

## Duplicate / legacy trees

| Path | Notes |
|------|--------|
| `core_secondary/` | Git may track this as a **single gitlink** (submodule-style). Do not develop here. |
| `data/core_secondary/` | Large mirrored copy of older layout. **Do not** treat as source of truth. |

### Recommended handling

1. **Search** for imports or docs referencing `core_secondary` before deletion.
2. If mirrors are **not required** for compliance backups: remove from the working tree and stop tracking (team decision).
3. If mirrors must remain: add a **README** at the duplicate root: “Deprecated mirror — do not edit.”

## Generated / sensitive files

| File | Action |
|------|--------|
| `data/marketing/leads.json` | **Gitignored** — created by `POST /api/leads`. Use `data/marketing/leads.json.example` as reference. |
| `data/generated/swarms/*.zip` | Build artifacts; safe to delete for disk hygiene; regenerate via Genesis Forge. |

## Staging cleanup in Git

After deleting deprecated files:

```bash
git add -u
git status
```

Review carefully before commit—especially under `data/` and `projects/`.
