# API endpoints

This document lists **HTTP(S) routes** defined in the primary codebase. Paths are as registered on the FastAPI application unless noted.

**Canonical backend app:** `orchestrator.src.core.api:app` (started via `scripts/run_server.py` or `npm start` / uvicorn).

---

## Primary FastAPI application (`orchestrator/src/core/api.py`)

| Method | Path | Handler | Purpose |
|--------|------|---------|---------|
| GET | `/` | `root` | Liveness-style JSON: API running message |
| GET | `/health` | `health_root` | Basic health + agent roster summary via `workforce` |
| GET | `/health/monetization` | `health_monetization` | DB, Redis/ARQ pool, and product catalog file checks |
| GET | `/health/readiness` | `health_readiness` | Orchestrator readiness flag |
| GET | `/health/liveness` | `health_liveness` | Simple liveness probe |
| POST | `/api/v1/fulfillment/generate-swarm` | `fulfill_swarm_order` | Stub fulfillment after purchase (returns download URL message) |
| GET | `/api/telemetry/stats` | `get_telemetry_stats` | In-memory telemetry counters (clicks, conversions, revenue, impressions) |
| GET | `/api/activity` | `get_activity` | Recent activity log entries (newest first, capped) |
| GET | `/api/integrations/status` | `get_integrations_status` | Stripe / Groq / database connectivity summary |
| POST | `/api/v1/analytics/event` | `record_analytics_event` | Persist analytics events via `SQLStore` when enabled |
| GET | `/products` | `get_products` | Product catalog from JSON and/or `monetization_engine` filters (`stage`, `recommendations_for`, `entry_only`) |
| GET | `/api/blog/posts` | `get_blog_posts` | List blog post metadata from `data/blog/posts.json` with markdown presence checks |
| GET | `/api/blog/posts/{slug}` | `get_blog_post` | Single post: metadata + markdown body from `data/blog/` or `docs/blog/` |
| GET | `/api/affiliates/track/{affiliate_code}` | `track_affiliate_click` | Log affiliate click in DB; returns JSON (no redirect yet) |
| GET | `/api/affiliates/high-ticket` | `get_high_ticket_affiliates` | Curated offers from `data/marketing/high_ticket_offers.json` |
| POST | `/api/tasks` | `post_api_tasks` | Runs `Orchestrator.submit_task_stream` to completion; optional `config` triggers Genesis Forge zip |
| POST | `/api/sovereign/launch` | `post_sovereign_launch` | Launch handshake; appends to activity log; optional `X-License-Key` header |
| POST | `/api/leads` | `post_lead` | Appends lead to gitignored `data/marketing/leads.json`; returns optional `guide_url` |
| POST | `/api/v1/monetization/webhook` | `unified_stripe_webhook` | Stripe webhook: signature verify, `checkout.session.completed` handling, profit ledger + telemetry |

### WebSockets (same app)

| Path | Handler | Purpose |
|------|---------|---------|
| `/ws/voice` | `voice_websocket` → `VoiceRouter.handle_connection` | Voice session (aligned with `tests/integration/test_voice_flow.py`) |
| `/ws/chamber` | `chamber_websocket` | Streams `activity_log` entries as `type: log` JSON for Chamber UI |

### Static file mounts (same app)

Starlette `StaticFiles` — effectively **GET** by URL prefix:

| Prefix | Directory | Purpose |
|--------|-----------|---------|
| `/assets` | `data/assets` | Uploaded/generated assets |
| `/marketing` | `data/marketing` | Marketing static files |
| `/swarms` | `data/generated/swarms` | Generated swarm packages |

---

## Alternate / standalone FastAPI apps (not the default `api:app`)

These define their own `FastAPI()` instances for **separate processes** or **code generation**, not the main uvicorn target unless explicitly run.

| Method | Path | Handler file | Purpose |
|--------|------|--------------|---------|
| GET | `/` | `orchestrator/src/core/traffic_manager.py` | Traffic manager root |
| GET | `/r` | `traffic_manager.py` | Redirect/statistics entry (traffic routing) |
| GET | `/stats` | `traffic_manager.py` | Traffic stats |
| GET | `/` | `orchestrator/src/agents/builder_agent.py` | **Generated** minimal app snippet for scaffolded projects |
| GET | `/health` | `builder_agent.py` | **Generated** health for scaffolded projects |

---

## Router module not mounted on main app

| Method | Path | Handler file | Purpose |
|--------|------|--------------|---------|
| POST | `/api/v1/monetization/webhook` | `orchestrator/src/core/monetization/webhooks.py` (`stripe_webhook`) | Alternate Stripe webhook implementation |

**Note:** `api.py` does **not** call `app.include_router(...)` for this module. The live webhook path is the handler in `api.py` above. The router file is a parallel/alternate implementation.

---

## Auxiliary script app (`scripts/stripe_webhook_listener.py`)

A **second** full FastAPI app used for local/testing or alternate entrypoints. Overlaps core routes and adds:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/user/jarvis` | Placeholder “user/Jarvis” endpoint (see file docstring) |

Other routes in this file largely mirror `api.py` (health, telemetry, products, blog, affiliates, monetization webhook).

---

## Frontend ↔ backend alignment

The Vite app uses **`getApiBase()` / `getWsBase()`** (`frontend/src/lib/apiBase.js`). In local dev, the API base is **same-origin** with proxy routes in `frontend/vite.config.js` (`/api`, `/assets`, `/marketing`, `/swarms` → FastAPI).

---

## MCP servers (`mcp_internal/servers/*/server.py`)

Not REST paths on port 8000. **FastMCP** processes expose **tools** over MCP (stdio JSON-RPC), for example:

- `mcp_internal/servers/stripe/server.py` — payment links, funnels, yield audit, affiliate tracking, etc.
- `mcp_internal/servers/outreach/server.py`, `oracle/server.py`, `swarm/server.py` — domain-specific tool surfaces

---

## Stripe CLI vs actual route

Root `package.json` script **`stripe:listen`** forwards to **`http://localhost:8000/api/v1/monetization/webhook`**, matching `unified_stripe_webhook` in `api.py`.
