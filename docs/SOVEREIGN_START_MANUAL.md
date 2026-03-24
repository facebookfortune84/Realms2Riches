# Sovereign Launch Manual (v8.0.1) - Industrial Matrix Initialization

## Objective
This manual outlines the procedure for launching the Realms2Riches Industrial Matrix locally using Docker Compose and the `SOVEREIGN_START.ps1` script. It ensures all core services, the autonomous agent workforce, and monitoring systems are initialized correctly for production-ready operation.

## Prerequisites
Before launching, ensure you have the following installed and configured:
-   **Python 3.11+**: With Poetry package manager.
-   **Docker Desktop**: Running and accessible on your system.
-   **Node.js & npm**: Required for frontend development/build processes if applicable.
-   **Git**: Essential for version control operations.
-   **Ngrok**: For securely exposing local backend services (required for testing external webhooks and remote access to the API).

## Environment Configuration

-   **Production Secrets (`.env.prod`):** This file MUST be populated with all necessary production API keys and credentials (approximately 70 variables). Refer to `docs/CONFIG.md` for a comprehensive list and explanations. **Crucially, ensure `STRIPE_WEBHOOK_SECRET` is set correctly.**
-   **Local Development (`.env.local`):** Use this file for local testing and development. The system prioritizes `.env.prod` when `ENV_MODE` is set to `prod` during runtime, but `.env.local` can override for local configurations.

## Launch Sequence (`SOVEREIGN_START.ps1`)

The `SOVEREIGN_START.ps1` script orchestrates the entire launch process. Execute it from the project root directory.

### 1. Preflight Checks & Environment Sync
-   **Dependency Verification:** Confirms Docker and Docker Compose installations are available.
-   **Environment Check:** Warns if `.env.prod` is missing, prompting the user to configure it.
-   **Process Cleanup:** Stops any lingering `python`, `uvicorn`, `arq`, or `docker` processes to prevent conflicts and ensure a clean startup.

### 2. Infrastructure Deployment (Docker Compose)
-   **Service Startup:** Executes `docker-compose -f infra/docker/docker-compose.yml up -d db redis adminer`.
    *   `db`: PostgreSQL database for persistent data storage.
    *   `redis`: Redis instance serving as the message broker for the ARQ task queue and caching.
    *   `adminer`: Web-based database management tool (accessible at `http://localhost:8080`).
-   **Database Readiness Assurance:** Includes a robust wait loop that polls the PostgreSQL container (`db` service) using `pg_isready` to ensure it's fully initialized and accepting connections before proceeding. This prevents race conditions during startup.
-   **Prune Option:** If the `$FullPrune` switch is used, performs a complete shutdown and removal of Docker resources (`docker-compose down -v --remove-orphans`).

### 3. Data Migration
-   **Legacy Data Import:** Executes `python scripts/migrate_json_to_postgres.py` to seamlessly import data from legacy JSON files into the new PostgreSQL database, ensuring data continuity.

### 4. Autonomous Agent Workforce (ARQ Worker)
-   **Worker Initialization:** Launches the ARQ worker using `python -m arq run orchestrator.src.core.worker.WorkerSettings`. This command ensures the worker connects to Redis and is ready to process asynchronous tasks.
-   **Process Isolation:** The worker is launched in a new, detached process (`-NoNewWindow`) for background operation.

### 5. Core API Activation
-   **API Server:** Starts the FastAPI application using `uvicorn orchestrator.src.core.api:app --host 0.0.0.0 --port 8000`.
    *   `--reload` is enabled for development; this should be removed for production deployments.
    *   The API will be accessible via Ngrok at the defined `BACKEND_URL` (`https://api.realms2riches.com`).

### 6. Continuous Outreach Daemon
-   **Outreach Service:** Launches the outreach daemon script using `python scripts/continuous_outreach_daemon.py` in a detached process for continuous lead processing and email outreach.

### 7. Finalizing & Verification
-   **Ngrok Tunnel:** If Ngrok is installed and the `BACKEND_URL` specifies a domain, attempts to start the Ngrok tunnel to expose the local API securely.
-   **Status Report:** Displays key URLs (API, Frontend, Adminer) for user reference and confirmation of active services.

## Operational Commands

-   **Start Services:** `.\SOVEREIGN_START.ps1`
-   **Stop Services:** `docker-compose -f infra/docker/docker-compose.yml down` (from the `infra/docker/` directory)
-   **View Logs:** `docker-compose -f infra/docker/docker-compose.yml logs -f`
-   **Run Migrations:** `python scripts/migrate_json_to_postgres.py`
-   **Test System Integrity:** `python scripts/test_system_integrity.py`

## Troubleshooting

-   **Database Connection Issues:** Ensure `POSTGRES_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, and `POSTGRES_HOST` are correctly set in `.env.prod`. Verify Docker container names match service names in `docker-compose.yml`.
-   **ARQ Worker Failures:** Check worker logs (`docker-compose logs worker`) and ensure dependencies are correctly installed.
-   **API Errors:** Review API logs (`docker-compose logs orchestrator`) for specific error messages.
-   **Ngrok Tunnel:** Ensure Ngrok is installed, authenticated, and its configuration matches the `BACKEND_URL` in `.env.prod`.

---
*Last Updated: March 10, 2026*
*Version: 8.0.1*
*Authored by: Realms2Riches AI Core*
