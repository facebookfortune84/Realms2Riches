# Realms2Riches - Environment Summary v5.2.0

## 1. Backend Stack
- **Framework**: FastAPI (Python 3.11+)
- **Main Entry Point**: `orchestrator/src/core/api.py`
- **Orchestration**: `orchestrator/src/core/orchestrator.py`
- **Configuration**: `.env.prod` (Pydantic settings)
- **Database**: SQLite (SQLAlchemy) and Vector Store (FAISS/In-memory)
- **Deployment**: ngrok for local tunneling (https://glowfly-sizeable-lazaro.ngrok-free.dev)

## 2. Frontend Stack
- **Framework**: React 18 (Vite, TypeScript)
- **Main Entry Point**: `projects/templates/landing-page/src/main.tsx`
- **Styling**: Tailwind CSS, Framer Motion
- **Deployment**: Vercel (https://frontend-two-xi-gal9lkptfi.vercel.app/)

## 3. Test & Quality Infrastructure
- **Unit/Integration**: `pytest` (invoked via `poetry run pytest`)
- **E2E/Live**: `playwright` (Python-based, `tests/e2e/test_live_frontend.py`)
- **Evidence**: `data/marketing/evidence/` (screenshots and logs)

## 4. Infrastructure & DevOps
- **Containers**: `docker-compose.yml` (if present)
- **Launch Script**: `ops/scripts/launch.ps1` (PowerShell)
- **Synchronization**: `infra/scripts/sync_cores.py` (Dual-core logic)
