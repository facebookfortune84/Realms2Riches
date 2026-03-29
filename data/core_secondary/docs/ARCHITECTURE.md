# Architecture Overview

## Mission Critical Objective
Realms2Riches is designed as a **Sovereign Autonomous Monetization Engine**, aiming to capture verifiable first payments and drive revenue across multiple monetization streams. The core objective is relentless execution and continuous verification of all deployed campaigns and features.

## Execution Environment
-   **Backend:** Python with FastAPI, running asynchronously with `asyncio`.
-   **Task Queue:** **ARQ** leveraging **Redis** for distributed, persistent, and scalable task management. This replaces direct script execution for many critical paths, ensuring reliability and retries.
-   **Database:** **PostgreSQL** for robust, relational data storage. Replaces previous file-based systems (`.json`) for leads, logs, and settings, ensuring data integrity and concurrent access.
-   **AI Core:** Integrated LLM providers (Groq default, OpenAI fallback) for agent reasoning, persona adoption, and dynamic content synthesis. Agents access tools defined in `data/oracle/tools/` and personas from `data/oracle/prompts/`.
-   **Infrastructure:** Containerized using **Docker Compose** (`infra/docker/docker-
compose.yml`) for local development and deployment. Services include Orchestrator, Worker, PostgreSQL, Redis, and Adminer, with health checks for reliability and resource limits for optimization.
-   **Frontend:** React-based interface utilizing `projects/templates/landing-page/` for user interaction, including the improved Genesis Forge for swarm configuration.

## Core Components

### 1. Orchestration Layer
-   **FastAPI Application (`orchestrator/src/core/api.py`):**
    -   Central API gateway for all external and internal interactions.
    -   Manages agent lifecycles and task dispatching.
    -   Provides WebSocket endpoints for real-time interaction (`/ws/voice`, `/ws/chamber`).
    -   Hosts `health`, `telemetry`, `activity` endpoints.
    -   Secured Stripe webhook listener (`/api/v1/monetization/webhook`) with signature verification.
    *   Exposes `/api/tasks` endpoint to trigger complex operations, including **Genesis Forge** swarm generation, passing detailed configurations (business type, industry, roles, tools, scale).
    -   Includes `RateLimitMiddleware` for API security.

### 2. Autonomous Workforce
-   **ARQ Worker (`orchestrator/src/core/worker.py`):**
    -   Manages background tasks asynchronously, replacing direct script calls for critical paths.
    -   Executes tasks like `personalized_outreach_task` (LLM-driven email synthesis) and `scrape_enrich_task` (lead processing and enqueuing).
    -   Connects to Redis for job queuing and PostgreSQL for task state persistence via `TaskResult` model.
    -   Utilizes `asyncio` for non-blocking operations.
-   **Agent (`orchestrator/src/core/agent.py`):**
    -   Represents individual specialized agents.
    -   Dynamically adopts personas from `PERSONA_LIBRARY` or `data/oracle/prompts/`.
    *   Executes tasks by selecting and running tools dynamically loaded from `self.tools` (derived from `data/oracle/tools/`).
    *   Integrates with memory (`VectorStore`) and records contributions via `lineage_registry`.

### 3. Data & Persistence
-   **PostgreSQL Database (`infra/docker/docker-compose.yml`):**
    -   Primary data store for `leads`, `outreach_logs`, `smtp_accounts`, `task_results`, `affiliates`, `affiliate_clicks`, and `commissions`.
    -   Ensured by `orchestrator/src/core/database.py` and `init_db()`.
-   **Redis:**
    -   Acts as the message broker for the ARQ task queue.
    -   Used for caching and ephemeral state management.

### 4. Monetization & Outreach
-   **Stripe Integration:**
    *   Handles `checkout.session.completed` and other critical events via `scripts/stripe_webhook_listener.py`.
    -   Automates fulfillment, including profit logging, affiliate commission attribution, and Genesis Forge dispatch.
    -   Secured using `STRIPE_API_KEY` and `STRIPE_WEBHOOK_SECRET` from `.env.prod`.
-   **Affiliate Program:**
    *   Models: `Affiliate`, `AffiliateClick`, `Commission` track referrals and revenue.
    *   `/api/affiliates/track/{affiliate_code}` endpoint logs clicks.
    *   Offers displayed in frontend (`HighTicketHub.jsx`). Links generated with tracking parameters.
-   **Outreach Daemon (`scripts/continuous_outreach_daemon.py`):**
    *   Polls for leads in `LeadStatus.SCRAPED` status.
    *   Enqueues `scrape_enrich_task` for processing.
    *   Manages lead status transitions (`SCRAPED` -> `QUEUED`).

### 5. Genesis Forge - Swarm Provisioning
-   **Backend (`orchestrator/src/core/genesis_forge.py`):**
    *   Dynamically generates custom swarm packages (`.zip`) based on user configuration (name, industry, roles, tools, scale).
    *   Packages include core framework files, custom `README.md`, `swarm_manifest.json`, and `.env.local`.
-   **Frontend (`projects/templates/landing-page/src/components/CompanyWizard.jsx`):**
    *   Provides a UI for selecting business type, agent personas (dynamically loaded from `data/oracle/prompts/`), and tools (dynamically loaded from `data/oracle/tools/`).
    *   Sends configuration to `/api/tasks` to trigger swarm generation.

### 6. Agent Interoperability & Tooling
-   **Oracle Directory (`data/oracle/`):** Contains persona prompts (`prompts/`) and tool definitions (`tools/`).
-   **Tool Integration:** Agents dynamically load and execute tools based on task requirements. `Agent.process_task` selects appropriate steps.
-   **Lineage Tracking:** `lineage_registry` records agent contributions and task provenance.

### 7. Infrastructure & Deployment
-   **Docker Compose (`infra/docker/docker-compose.yml`):** Manages containerized services (Orchestrator, Worker, DB, Redis, Adminer) with health checks and resource limits for reliability. Generated swarm packages are excluded from version control via `.gitignore`.
-   **Launch Script (`SOVEREIGN_START.ps1`):** Orchestrates local Docker startup, migrations, worker, API, outreach daemon, and Ngrok tunnel.
-   **Deployment:** Uses `dev` and `stasis` branches for Vercel staging and production deployments, respectively. Prioritizes `stasis` for production.

## Operational Workflow

1.  **Initiate Swarm:** User configures and provisions a swarm via Genesis Forge frontend.
2.  **Dispatch Task:** API (`/api/tasks`) receives request, enqueues task via ARQ/Redis.
3.  **Agent Execution:** Worker picks up task, assigns to agent, which formulates a plan and executes tools.
4.  **Monetization Loop:**
    *   Lead Extraction (`scripts/lead_extraction_swarm.py`) populates DB.
    *   Outreach Daemon polls for `SCRAPED` leads, enqueues `scrape_enrich_task`.
    *   Worker executes `scrape_enrich_task` (transitions status to `ENRICHED`, enqueues `personalized_outreach_task`).
    *   Worker executes `personalized_outreach_task` (LLM hook synthesis, email send, updates lead to `CONTACTED`).
    *   Stripe webhooks process payments, log revenue, attribute commissions, and trigger Genesis Forge if applicable.
5.  **Verification:** Continuous checks via `/health`, `/api/telemetry/stats`, `/api/activity`, and specific tests (`scripts/test_system_integrity.py`).

## Governance & Security

-   **Configuration:** `.env.prod` is the primary source for production secrets. `.env.example` and `.env.local` provide templates and local overrides. All ~70 variables are utilized.
-   **Security:** Webhook signature verification, rate limiting, and dependency auditing are implemented.
-   **Lineage:** Code provenance is tracked via `lineage_registry`.
-   **Testing:** Comprehensive tests (unit, integration, E2E), security, accessibility, and performance checks are mandatory for production readiness.

## Future Development
-   Advanced subscription management.
-   Agent-to-Agent commerce.
-   Enhanced reporting dashboards.
-   Automated competitive analysis.
-   Refined Git workflow with automated staging/production deployment triggers.