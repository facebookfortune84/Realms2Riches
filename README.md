# Agentic Software Development Agency

A fully autonomous, multi-agent system powered by **Groq** for high-speed agentic reasoning. Capable of generating complete, tested, and containerized software projects from high-level specifications, now with **Barge-In Voice** capabilities.

## Architecture

This system uses a "Chief Orchestrator" model where a primary agent delegates tasks to specialized sub-agents (Architect, Backend, Frontend, DevOps, QA, Growth, etc.).

### Key Features
- **LLM Provider**: Defaulting to Groq for sub-second inference.
- **Voice Mode**: Real-time WebSocket audio streaming with barge-in interruption.
- **Persistence**: Hybrid SQLite (Local) / Postgres (Production) with automatic fallback.
- **Marketing & Growth**: Config-driven brand identity for real-world campaign generation.
- **Governance**: Automated lineage tracking and SHA-256 artifact hashing.

## Quick Start

1. **Prerequisites**: Python 3.11+, Docker, Poetry.
2. **Setup**:
   ```bash
   cp .env.example .env
   # Fill in GROQ_API_KEY and BRAND_NAME in .env
   make setup
   ```
3. **Run API (Web/Voice)**:
   ```bash
   uvicorn orchestrator.src.core.api:app --reload
   ```
4. **Run CLI**:
   ```bash
   python -m orchestrator.src.core.orchestrator --submit projects/slots/my-app/spec.json
   ```

## Voice Support
Enable voice in `.env` with `VOICE_ENABLED=true`. 
See [Voice Runbook](docs/RUNBOOKS/RUNBOOK_VOICE_MODE.md) for details.

## Marketing & Social
Configure your brand identity in `.env` using `BRAND_NAME`, `MARKETING_SITE_URL`, etc.
See [Marketing Plan](docs/MARKETING_PLAN.md).

## Packaging
- **Docker**: Run `make docker-up` to start the full stack (Orchestrator, Worker, Postgres).
- **Executable**: (In development) See `infra/scripts/package_exe.sh`.

## Products & Pricing
The product catalog is sourced from `data/catalog/products.csv` and `prices.csv`.
To seed the database:
   ```bash
   python -m orchestrator.src.core.catalog.ingest
   ```

## Documentation
- [Architecture](docs/ARCHITECTURE.md)
- [Agents](docs/AGENTS.md)
- [Governance](docs/GOVERNANCE.md)
- [Launch Checklist](docs/RUNBOOKS/RUNBOOK_LAUNCH_CHECKLIST.md)
