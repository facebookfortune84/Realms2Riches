# Realms2Riches Sovereign Matrix - Lineage & Architecture Map

## 1. System Origins
- **Project Root:** `F:\Realms2Riches`
- **Core Engine:** `orchestrator.src.core.orchestrator.Orchestrator`
- **Monetization Engine:** `orchestrator.src.core.monetization.engine.MonetizationEngine`
- **Primary Data Store:** PostgreSQL (`app_db`) + Vector RAG (`sovereign_memory.json`)

## 2. Module Dependencies
### Core Infrastructure
- `orchestrator.src.core.api` -> Depends on `Orchestrator`, `MonetizationEngine`
- `orchestrator.src.core.scheduler` -> Depends on `SocialMediaMultiplexer`, `MonetizationEngine`
- `orchestrator.src.core.self_healing` -> Depends on `settings`, `sqlite3`

### External Integrations
- **Stripe:** `stripe` (Payments, Products)
- **Groq:** `groq` (LLM Intelligence)
- **OpenAI:** `openai` (Fallback LLM)
- **Google:** `google-auth`, `google-api-python-client` (Gmail, Drive)
- **Ngrok:** `pyngrok` (Tunnels)

## 3. Data Flow
1.  **Ingestion:** `scripts/lead_extraction_swarm.py` -> Scrapes Data -> `data/customers/yc_targets.json`
2.  **Processing:** `Orchestrator` -> Assigns Tasks -> `Agents` (Personalized)
3.  **Action:** `Agents` -> Execute Tools (`outreach`, `seo_factory`) -> External APIs
4.  **Verification:** `scripts/verify_first_payment.py` -> Polls Stripe -> Logs Success
5.  **Healing:** `SelfHealingService` -> Monitors `data/*` -> Restores Baseline

## 4. Execution Order (Launch Sequence)
1.  **Environment Check:** `SOVEREIGN_START.ps1` checks Docker/Git.
2.  **Database Init:** PostgreSQL starts, schema verified by `SelfHealingService`.
3.  **API Launch:** `uvicorn orchestrator.src.core.api:app` (Port 8000).
4.  **Tunneling:** `ngrok http 8000` (Manual or Scripted).
5.  **Swarm Activation:** `scripts/yolo_mode_monetization.py` triggers `MonetizationEngine`.

## 5. Security & Risks
- **Secrets:** `.env.prod`, `.env.local` must be GitIgnored.
- **API Keys:** Stripe, Groq, OpenAI keys stored in `.env`.
- **Exposed Ports:** 8000 (API), 5432 (Postgres). Ensure firewall rules apply.
- **Ngrok:** Public tunnel bypasses local firewalls. Monitor access logs.

## 6. Areas for Immediate Remediation
- **Hardcoded Paths:** Some scripts reference `F:\Realms2Riches` directly. Relative paths preferred.
- **Error Handling:** `Agent` JSON parsing is brittle (fixed in `dev` via retry logic).
- **Stubbed Streams:** Streams 1-10 in `MonetizationEngine` operate in simulation mode (logging only). Implementation required for full efficacy.
