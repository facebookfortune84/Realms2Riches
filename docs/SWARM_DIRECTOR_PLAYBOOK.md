# Swarm director playbook (stay high-level)

You steer outcomes; agents and workers implement. This playbook minimizes hands-on full-stack work while keeping quality bar high.

## 1. Define the slice

- One **outcome** per swarm turn (e.g. “wire Chamber WebSocket”, “fix Stripe forward URL”).
- Point agents to **PATH_FORWARD.md**, **architecture/** docs, and the **exact files** to touch.
- Forbid open-ended “refactor the repo” unless a dedicated cleanup task exists.

## 2. Contracts before code

- **API contract:** method, path, request shape, response shape, errors.
- **UI contract:** which component calls which endpoint; use `getApiBase()` / `getWsBase()` only (see `frontend/src/lib/apiBase.js`).
- **Verification:** pytest targets or manual curl/WebSocket checks.

## 3. Execution pattern

1. Agent reads relevant files (not the whole monorepo).
2. Agent implements and runs **pytest** (or the narrowest script).
3. Agent updates **Taskmaster** subtask notes and marks status.
4. You review **diff size** and **risk** (billing, auth, deletes).

## 4. Delegation prompts that work

- “Implement `POST /api/...` per PATH_FORWARD; update `api-endpoints.md`; run `pytest tests/integration/test_*.py`.”
- “Frontend: replace raw `import.meta.env` URLs with `getApiBase()`; do not change copy.”
- “Docs only: align ARCHITECTURE.md with `docs/architecture/`; no code.”

## 5. What not to do

- Do not edit **`core_secondary/`** or **`data/core_secondary/`** for product features.
- Do not add a second Stripe webhook implementation on the same path without removing the first.
- Do not commit **`data/marketing/leads.json`** (gitignored); use `leads.json.example` as a template.

## 6. Signals you are doing too much hands-on dev

- You are picking import orders and fixing lints personally every day.
- Agents repeatedly miss the same missing endpoint—fix the **contract doc** and add a test.
- You merge without a **one-line outcome** description—reinstate the director checklist above.

## 7. Optional automation

- CI: `poetry run pytest tests/` + `npm run build --prefix frontend` on PRs.
- Pre-commit: `prettier` on `frontend/`, `ruff` on `orchestrator/` if introduced later—keep scope small when adding.
