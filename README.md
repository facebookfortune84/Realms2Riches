# Realms2Riches: Sovereign AI Orchestrator - Production Ready

## Mission Statement
Empowering businesses with industrial-grade autonomous agent swarms, designed for verifiable monetization and self-scaling operations. We aim to transform complex operational tasks into fully automated revenue streams.

## Architecture Overview

The system is built on a robust, multi-layered architecture comprising:
*   **Core Orchestration:** A central FastAPI application (`orchestrator/src/core/api.py`) managing agent lifecycles, task dispatching, and API endpoints. Includes enhanced Stripe webhook handling and affiliate tracking.
*   **Distributed Workforce:** Utilizes **ARQ** with **Redis** as a broker for asynchronous task execution, enabling high concurrency and reliable background processing.
*   **Sovereign Intelligence:** Leverages Groq (default) or OpenAI LLMs for agent reasoning, persona adoption, and dynamic content/hook generation. Tools from `data/oracle/tools` and personas from `data/oracle/prompts` are integrated.
*   **Persistence Layer:** Configurable database support (PostgreSQL via SQLAlchemy/asyncpg, with SQLite fallback) for managing leads, logs, task results, commissions, and system state.
*   **Genesis Forge:** A dynamic swarm provisioning engine that generates custom, downloadable swarm packages based on user selections (industry, roles, tools, scale).
*   **Monetization Integration:** Deep integration with Stripe for payment capture, automated fulfillment, and affiliate commission tracking.
*   **Communication:** Supports multi-channel outreach (Email, LinkedIn), voice interaction via WebSockets, and real-time activity streaming.

## Key Features

### 🚀 Autonomous Monetization Engine
- **End-to-End Workflows:** From lead scraping and enrichment to personalized outreach and payment capture.
- **Direct Revenue Capture:** Integrated Stripe checkout and webhook processing for immediate sales verification.
- **Affiliate Network:** Robust system for positioning high-ticket offers, tracking clicks, and attributing commissions via unique codes and backend logging.
- **Profit Ledger:** Real-time tracking of revenue and expenses, including affiliate commissions.

### 🧠 Cognitive Agent Swarms
- **Massive Scale:** Designed to support swarms of 1000+ specialized agents.
- **Persona & Tool Integration:** Agents dynamically adopt personas from `data/oracle/prompts/` and utilize tools defined in `data/oracle/tools/`.
*   **LLM-Powered Synthesis:** Personalized email hooks and dynamic content generation.

### 🛠️ Genesis Forge - Swarm Vending
- **Custom Swarm Packages:** Generate and download fully functional, deployable swarm artifacts.
- **User-Configurable:** Select business types, agent roles (personas), tools, and scale density.
- **Production-Ready Output:** Includes core operating files, launch scripts (`SOVEREIGN_START.ps1`), custom READMEs, and `.env.local` configuration.

### 🔒 Industrial Grade Security & Reliability
- **Secure Webhooks:** Verified Stripe webhook listener with signature validation.
- **Rate Limiting:** Implemented for API endpoints.
- **Robust Infrastructure:** Dockerized services (Postgres, Redis) with health checks and resource limits.
- **Autonomous Recovery:** Agents designed to handle failures and resume operations.

## Quick Start (Local Docker Setup)

1.  **Prerequisites**:
    *   Python 3.11+
    *   Docker Desktop
    *   Poetry
    *   Node.js & npm (for frontend development)

2.  **Configuration**:
    *   Copy `.env.example` to `.env.prod` and fill in all necessary production API keys and credentials (approx. 70 variables). Refer to `docs/CONFIG.md` for details. **Crucially, ensure STRIPE_WEBHOOK_SECRET is set.**
    *   Ensure `.env.prod` is loaded correctly by services (handled by `docker-compose.yml` via environment variable interpolation).

3.  **Initialize & Migrate**:
    ```bash
    # Ensure your .env.prod file is populated and accessible to docker-compose
    # Use 'make setup' if available or run commands manually
    # Example manual steps:
    docker-compose -f infra/docker/docker-compose.yml up -d db redis
    # Wait for DB to be ready (check logs or use script)
    python scripts/migrate_json_to_postgres.py
    ```

4.  **Launch Services**:
    ```powershell
    # Navigate to project root
    cd F:\Realms2Riches 

    # Execute the main launch script
    .\SOVEREIGN_START.ps1 
    ```
    This script will:
    *   Start Docker infrastructure (Postgres, Redis, Adminer).
    *   Run database migrations.
    *   Launch the ARQ Worker.
    *   Start the FastAPI API.
    *   Initiate the Continuous Outreach Daemon.
    *   Configure and start Ngrok for the backend URL.

5.  **Access Services**:
    *   API: `https://api.realms2riches.com` (or `http://localhost:8000` locally)
    *   Frontend: `https://realms2riches.com`
    *   Adminer (DB GUI): `http://localhost:8080`
    *   Chamber (Activity Log): `http://localhost:8000/ws/chamber` (Connect via WebSocket)

## Genesis Forge - Swarm Provisioning

Users can configure and provision custom agent swarms via the frontend interface:
1.  **Define Identity**: Enter company name and select operational sector.
2.  **Select Architecture**: Choose agent personas (roles) and active toolsets.
3.  **Set Scale**: Define the number of agent units.
4.  **Provision**: Generate and download a tailored swarm package (`.zip`) containing all necessary files and configurations.

## Monetization Streams

The system supports multiple monetization avenues:
-   **Direct Sales**: Via Stripe integration and `checkout.session.completed` webhook fulfillment.
-   **Affiliate Marketing**: Trackable links and commission attribution for high-ticket offers integrated via the backend API and frontend display.
-   **SaaS Subscriptions**: (Future development) via Stripe subscription events.
-   **Agent-as-a-Service**: (Future development) Agents offering specialized services via AgentProtocol.

## Documentation

*   [Architecture Overview](docs/ARCHITECTURE.md)
*   [Agent Personas & Tooling](docs/AGENTS.md)
*   [Sovereign Governance](docs/GOVERNANCE.md)
*   [Stripe Webhook Setup SOP](docs/oracle/sop/TEC_011_STRIPE_WEBHOOK_SETUP.md)
*   [Developer Runbook](docs/RUNBOOKS/RUNBOOK_DEV.md)
*   [Configuration Guide](docs/CONFIG.md)

## Git Workflow & Deployment

-   **Repository Structure:** Root directory organization ensures clarity. Generated files (e.g., `data/generated/swarms`) are managed outside version control.
-   **Branches:** Use `dev` for active development, `stasis` for production-ready releases.
-   **Commits:** Follow Conventional Commits standard.
-   **Tagging:** Use semantic versioning tags (e.g., `v1.0.0`).
*   **Vercel Deployment:** Configure `stasis` branch as the production deployment target. `dev` branch may deploy to a staging environment.
*   **Lineage Tracking:** `lineage.py` tracks code provenance. Run `make lineage` after major changes.

## Contributing

Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

*   Never expose sensitive credentials. Use `.env.prod` and Docker secrets management.
*   Verify all external API interactions and webhook sources.
*   Regularly audit dependencies for vulnerabilities.
*   See [SECURITY.md](SECURITY.md) for detailed practices.

