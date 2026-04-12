# Feature map

Mapping **business / product features** to the **primary implementation files** in the canonical repo (root `orchestrator/`, `frontend/`, `scripts/`, `mcp_internal/`, `data/`). Listed files are the main touchpoints, not exhaustive line coverage.

---

## HTTP API surface (cross-cutting)

| Feature area | Backend | Notes |
|--------------|---------|-------|
| Routing, CORS, rate limit, static mounts | `orchestrator/src/core/api.py` | Single FastAPI app |
| Health / probes | `api.py` | `/health`, `/health/monetization`, readiness, liveness |
| Swarm task dispatch (SPA) | `api.py` | `POST /api/tasks` → `Orchestrator.submit_task_stream`; optional Genesis Forge when `config` present |
| Sovereign launch handshake | `api.py` | `POST /api/sovereign/launch` |
| Lead capture | `api.py` | `POST /api/leads` → appends JSON (gitignored); guide text `data/marketing/SOVEREIGN_GUIDE.txt` |
| High-ticket offers feed | `api.py` | `GET /api/affiliates/high-ticket` → `data/marketing/high_ticket_offers.json` |
| Voice + Chamber sockets | `api.py` | `/ws/voice`, `/ws/chamber` |

---

## Monetization & payments

| Capability | Files |
|------------|-------|
| Stripe webhook, checkout completion, profit ledger, telemetry bump | `orchestrator/src/core/api.py` (`unified_stripe_webhook`, `fulfill_order`) |
| Alternate webhook router (not mounted on main app) | `orchestrator/src/core/monetization/webhooks.py` |
| Funnel engine, recommendations, staged products | `orchestrator/src/core/monetization/engine.py` |
| Product catalog (DB + JSON slots) | `orchestrator/src/core/catalog/api.py`, `orchestrator/src/core/catalog/models.py`, `orchestrator/src/core/catalog/ingest.py`, `data/catalog/products.json`, `data/store/slots/*.json` |
| Revenue / payment **tools** for agents | `orchestrator/src/tools/revenue_tools.py` |
| MCP: Stripe-like monetization tools | `mcp_internal/servers/stripe/server.py` |
| Scripts: Stripe catalog, webhooks, verification | `scripts/stripe_webhook_listener.py`, `scripts/verify_*`, `scripts/create_new_stripe_products.py`, `scripts/migrate_stripe_products.py` |

---

## Product catalog & storefront (UX)

| Capability | Files |
|------------|-------|
| Pricing / catalog fetch UI | `frontend/src/pages/Pricing.jsx` |
| Store page | `frontend/src/pages/Store.jsx` |
| Default public API URL | `frontend/src/config.js` |

---

## Blog & content

| Capability | Files |
|------------|-------|
| List/detail API | `orchestrator/src/core/api.py` (`get_blog_posts`, `get_blog_post`) |
| Blog index and post pages | `frontend/src/pages/Blog.jsx`, `frontend/src/pages/BlogPost.jsx` |
| CMS-style helpers in template | `frontend/src/lib/cms.js` |
| Population / generation scripts | `scripts/populate_amazing_blog.py`, `scripts/generate_seo_metadata.py` |
| Content data | `data/blog/posts.json`, `data/blog/*.md`, `docs/blog/*.md` |

---

## Affiliates

| Capability | Files |
|------------|-------|
| Click tracking API | `orchestrator/src/core/api.py`, `orchestrator/src/core/models.py` (`Affiliate`, `AffiliateClick`) |
| Affiliates marketing page | `frontend/src/pages/Affiliates.jsx` |
| Disclosure / compliance pages | `frontend/src/pages/AffiliateDisclosure.jsx` |
| “High ticket hub” UI (**calls backend path not in main `api.py`**) | `frontend/src/pages/HighTicketHub.jsx` |
| Affiliate tools (agent/MCP) | `orchestrator/src/tools/revenue_tools.py`, `mcp_internal/servers/stripe/server.py` |

---

## Analytics & telemetry

| Capability | Files |
|------------|-------|
| Event ingestion API | `orchestrator/src/core/api.py` |
| In-memory telemetry + activity log | `orchestrator/src/core/api.py` (module globals) |
| Client analytics helper | `frontend/src/lib/analytics.js` |
| SQL persistence for events | `orchestrator/src/memory/sql_store.py` |
| Logging / telemetry utilities | `orchestrator/src/logging/logger.py`, `orchestrator/src/logging/telemetry.py` |
| Console dashboards | `frontend/src/pages/UnifiedConsole.jsx`, `frontend/src/pages/Dashboard.jsx` |

---

## Autonomous agents & orchestration

| Capability | Files |
|------------|-------|
| Central coordinator, tool wiring, cells, backlog, scheduler | `orchestrator/src/core/orchestrator.py` |
| Single agent execution unit | `orchestrator/src/core/agent.py` |
| LLM provider (Groq) | `orchestrator/src/core/llm_provider.py` |
| Agent fleet generation | `orchestrator/src/agents/fleet.py`, `orchestrator/src/agents/implementations.py` |
| Personas / prompts | `orchestrator/src/agents/persona_library.py`, `orchestrator/src/agents/prompts.py` |
| Content / funnel / builder agents | `orchestrator/src/agents/content_factory.py`, `funnel_architect.py`, `builder_agent.py` |
| Autonomous task stream | `orchestrator/src/core/backlog.py` |
| Workforce / agent dossiers | `orchestrator/src/core/workforce.py` |
| Governance / ticketing | `orchestrator/src/core/ticketing/governance.py`, `ticketing/system.py` |
| Self-healing maintenance tasks | `orchestrator/src/core/self_healing.py` |
| Validation / audits | `orchestrator/src/validation/*.py` |
| **Task submission HTTP** | *Not implemented on `api.py`* — UI references `/api/tasks` in `frontend/src/pages/Home.jsx`, `Cockpit.jsx`, `UnifiedConsole.jsx`, `components/CompanyWizard.jsx` |

---

## Outreach & email campaigns

| Capability | Files |
|------------|-------|
| Campaign definitions, templates, enqueue | `orchestrator/src/core/outreach/campaigns.py` |
| SMTP tool | `orchestrator/src/tools/smtp_tools.py` |
| Redis / ARQ enqueue from orchestrator | `orchestrator/src/core/orchestrator.py` |
| Worker consumer | `orchestrator/src/core/worker.py` |
| SMTP / outreach config | `orchestrator/src/core/outreach/config.py`, `outreach/smtp.py` |
| MCP outreach server | `mcp_internal/servers/outreach/server.py` |
| Long-running outreach scripts | `scripts/continuous_outreach_daemon.py`, `scripts/inbox_*`, `scripts/ycombinator_outreach_swarm.py`, … |

---

## Voice & multimodal

| Capability | Files |
|------------|-------|
| WebSocket session handling (logic) | `orchestrator/src/core/voice/router.py`, `session.py` |
| STT/TTS adapters | `orchestrator/src/core/voice/interfaces.py`, `mock_adapters.py`, `real_adapters.py` |
| Voice tools for agents | `orchestrator/src/tools/voice_tools.py` |
| Tests expecting `/ws/voice` | `tests/integration/test_voice_flow.py` |

---

## Swarm packaging & “genesis” delivery

| Capability | Files |
|------------|-------|
| Zip / swarm generation | `orchestrator/src/core/genesis_forge.py` |
| Fulfillment stub HTTP | `orchestrator/src/core/api.py` (`/api/v1/fulfillment/generate-swarm`) |
| Served artifacts | `data/generated/swarms/` (mounted at `/swarms`) |
| MCP swarm server | `mcp_internal/servers/swarm/server.py` |
| Bundling scripts | `scripts/sovereign_bundler.py`, `scripts/bundle_splitter.py` |

---

## Traffic routing (optional standalone)

| Capability | Files |
|------------|-------|
| Redirect / stats mini-service | `orchestrator/src/core/traffic_manager.py` |

---

## Licensing, oracle, forge (supporting “sovereign” product)

| Capability | Files |
|------------|-------|
| Licensing helpers | `orchestrator/src/core/licensing.py` |
| Oracle advisor | `orchestrator/src/core/oracle_advisor.py` |
| Forge orchestration | `orchestrator/src/core/forge_orchestrator.py` |
| MCP oracle server | `mcp_internal/servers/oracle/server.py` |
| Launch UI (**POST `/api/sovereign/launch` not on main `api.py`**) | `frontend/src/pages/LaunchControl.jsx` |

---

## Lead capture

| Capability | Files |
|------------|-------|
| Lead popup UI (**POST `/api/leads` not on main `api.py`**) | `frontend/src/components/LeadGenPopup.jsx` |
| Lead scraping tools | `orchestrator/src/tools/lead_scraper.py` |

---

## Marketing site shell

| Capability | Files |
|------------|-------|
| Routes, chrome (nav, footer, cookies) | `frontend/src/App.jsx`, `components/Navbar.jsx`, `Footer.jsx`, `CookieBanner.jsx` |
| Legal pages | `frontend/src/pages/PrivacyPolicy.jsx`, `TermsOfService.jsx` |
| Success / cancel post-checkout | `frontend/src/pages/Success.jsx`, `Cancel.jsx` |
| Analytics | `frontend/src/lib/analytics.js` |

---

## Infrastructure & ops

| Capability | Files |
|------------|-------|
| Compose stack | `infra/docker/docker-compose.yml`, `docker-compose.prod.yml` |
| Images | `infra/docker/Dockerfile.orchestrator`, `Dockerfile.worker` |
| Environment / settings | `orchestrator/src/core/config.py`, `.env.example` (if present at root) |

---

## Tests (feature safety nets)

| Area | Files |
|------|-------|
| API integration | `tests/integration/test_api_endpoints.py` |
| Voice flow | `tests/integration/test_voice_flow.py` |
| Other | `tests/` tree |

---

## How to use this map

- **Implementing a feature:** start from the row’s backend files, then the matching `frontend/src/pages` or `components`.
- **Fixing API/UX mismatches:** compare `docs/architecture/api-endpoints.md` with `frontend/src/**/*.jsx` `fetch()` calls.
- **Avoiding duplicate work:** ignore `core_secondary/` and `data/core_secondary/` unless you explicitly maintain those syncs.
