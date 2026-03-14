# Realms2Riches - Launch Manual (v5.0.0-PLATINUM)

**Status:** READY FOR DEPLOYMENT
**Branch:** `dev` (Active), `stasis` (Backup Snapshot)

## 1. Prerequisites
Before initiating the Sovereign Matrix, ensure the following are installed and configured:
- **Python 3.10+**: Core runtime.
- **Docker Desktop**: Required for `SOVEREIGN_START.ps1` full stack deployment.
- **Ngrok**: Required for public tunneling (`infra/tools/ngrok/ngrok.exe`).
- **PostgreSQL**: (Optional if running locally without Docker).

## 2. Environment Configuration
Ensure `.env.prod` or `.env.local` contains valid API keys for:
- `GROQ_API_KEY` (Intelligence)
- `STRIPE_API_KEY` (Monetization)
- `OPENAI_API_KEY` (Fallback)

## 3. Launch Methods

### A. Production Launch (Docker - Recommended)
This method launches the entire infrastructure (API, DB, Worker) in isolated containers, rebuilding only when necessary.
1. Open PowerShell as Administrator.
2. Run:
   ```powershell
   .\SOVEREIGN_START.ps1
   ```
   *Note: This script enforces production mode, builds Docker images (if code/dependencies changed), and verifies health at the public URL.*

### B. Force Rebuild
If you need to ensure a completely fresh build (e.g., after significant dependency changes):
```powershell
.\SOVEREIGN_START.ps1 -Prune
```

### B. Local Development (No Docker)
Use this method for rapid testing or debugging.
**Terminal 1 (API Server):**
```powershell
$env:PYTHONPATH="."
uvicorn orchestrator.src.core.api:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 (Tunneling):**
```powershell
.\infra\tools\ngrok\ngrok.exe http 8000
```
*Copy the public URL (e.g., https://xyz.ngrok-free.app) for webhooks.*

**Terminal 3 (Swarm Activation):**
```powershell
$env:PYTHONPATH="."
python scripts/yolo_mode_monetization.py
```

## 4. Verification
1. **Health Check:** Visit `https://glowfly-sizeable-lazaro.ngrok-free.dev/health`. Status should be `ok`.
2. **Payment Monitoring:**
   ```powershell
   $env:PYTHONPATH="."
   python scripts/verify_first_payment.py
   ```
   *This script polls Stripe for live transactions.*

## 5. Troubleshooting
- **Missing Dependencies:** Run `pip install -r requirements.txt`.
- **Database Errors:** The `SelfHealingService` will attempt to patch schemas on startup. Check logs.
- **Ngrok Issues:** Ensure the tunnel is active before starting external webhooks.

## 6. Next Steps
- Monitor `data/logs` for agent activity.
- Review `LINEAGE.md` for architecture details.
- Commit changes to `dev` branch only. `stasis` is locked.
