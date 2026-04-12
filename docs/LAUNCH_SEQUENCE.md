# Launch sequence (operator checklist)

This sequence assumes Docker or `poetry run uvicorn orchestrator.src.core.api:app` for the API and `npm run dev --prefix frontend` for the UI. Adjust hosts if you deploy behind IIS or a reverse proxy.

## Phase 0 — Repository and safety

1. Confirm `.cursor/mcp.json` is **not** tracked (`git check-ignore -v .cursor/mcp.json`). Use `.cursor/mcp.json.example` and copy to `mcp.json` locally only.
2. Run `npm run lineage:lock` before tagging a release so artifact hashes are recorded.
3. Ensure `data/marketing/leads.json` is absent from git (use `leads.json.example`); never commit live lead files.

## Phase 1 — CI and tests (automatable)

1. `poetry install`
2. `poetry run pytest tests/integration/ -q` (expand to full `tests/` when secrets and external services are stubbed).
3. `npm ci --prefix frontend` then `npm run build --prefix frontend`.

## Phase 2 — Staging environment

1. Point staging `DATABASE_URL` / Redis at non-production resources.
2. Set `STRIPE_TEST_MODE=YES` and use Stripe test keys; run `npm run stripe:listen` against the **same** webhook path the backend exposes (`/api/v1/monetization/webhook`).
3. Smoke-test: health, `POST /api/tasks`, WebSocket `/ws/voice` (if voice stack enabled), dashboard pages that call `/api`.

## Phase 3 — Production cutover (human-gated)

1. Legal: Terms, privacy, refund policy, affiliate disclosures where applicable.
2. Stripe: live products and prices, webhook signing secret in server env only.
3. DNS and TLS for `api.*` and marketing domains.
4. Rotate any credential that ever lived in a tracked file or chat log.

## Phase 4 — Post-launch

1. Enable observability (logs, uptime checks) on the API.
2. Weekly review of `docs/DRIFT_PREVENTION.md` and Taskmaster `next` for runway tasks.
