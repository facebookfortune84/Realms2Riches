# PRD: Launch, monetization, and operator runway (v1)

## Goal

Ship a **reviewable, testable** Realms2Riches stack: FastAPI orchestrator, Vite frontend, Stripe monetization hooks, and documentation sufficient for a human operator to complete legal and DNS steps.

## Non-goals

- Replacing the operator for Stripe live account verification, domain purchase, or counsel-reviewed legal pages.
- Fully automated cold email at scale without human approval of copy and lists (see `docs/marketing/COLD_OUTREACH_SOP_v2.md`).

## Requirements

1. **API**: Documented REST and WebSocket routes; health summary; monetization webhook path consistent with `package.json` `stripe:listen`.
2. **Frontend**: Build succeeds; API calls use `getApiBase()` / proxy in dev; no hard-coded production secrets in source.
3. **Tests**: Integration tests pass in CI for API + critical paths; frontend build job passes.
4. **SOP alignment**: Outreach and monetization behavior must respect dry-run flags until the operator explicitly enables production sending and billing.
5. **Task tracking**: Maintain `.taskmaster/tasks/tasks.json` with launch tasks; use file storage (`storage.type: file` in `.taskmaster/config.json`).

## Success metrics

- CI green on `main` for backend tests + frontend build.
- Staging can complete a test checkout or webhook test event end-to-end.
- Operator checklist in `docs/LAUNCH_SEQUENCE.md` completed for production.

## References

- `docs/marketing/COLD_OUTREACH_SOP_v2.md`
- `docs/LAUNCH_SEQUENCE.md`
- `docs/DRIFT_PREVENTION.md`
- `docs/architecture/api-endpoints.md`
