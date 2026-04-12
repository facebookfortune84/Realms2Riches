# Realms2Riches — PRODUCTION LAUNCH PROTOCOL (v1.0.1 / Windows Server 2025 + IIS)

> Canonical deployment target: **Windows Server 2025 + IIS** (HTTPS termination) + **Python backend via IIS HttpPlatformHandler or nssm service** + **React static build served by IIS**.  
> WSL2 is the **dev** environment only. No Docker in production.

---

## Pre-Launch Checklist

Run the readiness script from PowerShell:

```powershell
Set-Location C:\Realms2Riches
python scripts\readiness_proofs.py
```

All checks must return **PASS** before proceeding.

---

## Step 1 — Backend Service (IIS + HttpPlatformHandler or nssm)

### Option A — nssm (recommended for simplicity)

```powershell
# Install nssm if not present: https://nssm.cc/download
nssm install R2R-API "C:\Realms2Riches\.venv\Scripts\python.exe"
nssm set R2R-API AppParameters "-m uvicorn orchestrator.src.core.api:app --host 127.0.0.1 --port 8000"
nssm set R2R-API AppDirectory "C:\Realms2Riches"
nssm set R2R-API AppEnvironmentExtra "PYTHONPATH=C:\Realms2Riches"
nssm start R2R-API
```

Verify:
```powershell
Invoke-WebRequest -Uri http://127.0.0.1:8000/health -UseBasicParsing | Select-Object StatusCode
# Expected: 200
```

### Option B — IIS HttpPlatformHandler

1. Install [HttpPlatformHandler v1.2](https://www.iis.net/downloads/microsoft/httpplatformhandler) on IIS.
2. Create site `R2R-API` pointing to `C:\Realms2Riches`.
3. Use `web.config` in repo root (see `infra/iis/web.config.example` — create if absent).

---

## Step 2 — Frontend Static Build

```powershell
# Build
npm ci --prefix frontend
npm run build --prefix frontend
# Output: frontend\dist\

# IIS: create site R2R-Frontend pointing to C:\Realms2Riches\frontend\dist
# Set default document to index.html
# Add URL Rewrite rule: all requests → /index.html (SPA fallback)
```

IIS URL Rewrite rule snippet for `web.config` in `frontend\dist\`:

```xml
<rewrite>
  <rules>
    <rule name="SPA Fallback" stopProcessing="true">
      <match url=".*" />
      <conditions logicalGrouping="MatchAll">
        <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
        <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
      </conditions>
      <action type="Rewrite" url="/index.html" />
    </rule>
  </rules>
</rewrite>
```

---

## Step 3 — Environment Variables (Production)

Set in IIS site → Configuration Editor → `system.webServer/httpPlatform/environmentVariables`  
**OR** in the nssm service with `nssm set R2R-API AppEnvironmentExtra`:

```
DATABASE_URL=postgresql://user:pass@localhost/r2r_prod
STRIPE_SECRET_KEY=sk_live_...        # Never in git
STRIPE_WEBHOOK_SECRET=whsec_...      # Never in git
STRIPE_TEST_MODE=NO
TELEMETRY_ENABLED=true
ANALYTICS_ENABLED=true
VITE_API_URL=https://api.realms2riches.com
```

> **Security:** Rotate any key that was ever committed to git or pasted in chat before using in production.

---

## Step 4 — DNS and TLS

| Subdomain | Target | Certificate |
|-----------|--------|-------------|
| `realms2riches.com` | IIS site for `frontend\dist` | Let's Encrypt via win-acme or purchased cert |
| `api.realms2riches.com` | IIS reverse proxy → `127.0.0.1:8000` | Same cert or dedicated |

```powershell
# Verify TLS after DNS propagates
Invoke-WebRequest -Uri https://api.realms2riches.com/health -UseBasicParsing | Select-Object StatusCode
# Expected: 200
```

---

## Step 5 — Stripe Webhook Registration

1. In Stripe Dashboard → Developers → Webhooks → Add endpoint:
   - URL: `https://api.realms2riches.com/api/v1/monetization/webhook`
   - Events: `checkout.session.completed`, `payment_intent.succeeded`, `customer.subscription.created`
2. Copy the **Webhook Signing Secret** (`whsec_...`) into `STRIPE_WEBHOOK_SECRET` environment variable.
3. Verify with a test event from Stripe Dashboard → sends 200 response.

---

## Step 6 — Lineage Lock and Tag

```powershell
Set-Location C:\Realms2Riches
python infra\scripts\hash_registry.py   # Lock artifact hashes

git tag -a v1.0.1 -m "Production launch v1.0.1"
# Then push from a machine with GitHub auth:
git push origin main --tags
```

---

## Step 7 — Post-Launch Monitoring

| Check | Command / URL |
|-------|---------------|
| API health | `https://api.realms2riches.com/health` |
| Monetization health | `https://api.realms2riches.com/health/monetization` |
| Swarm transparency | `https://api.realms2riches.com/api/v1/swarm/transparency` |
| Windows Event Log | Event Viewer → Application → filter source `R2R-API` |
| Uptime alert | Configure UptimeRobot or Azure Monitor on `/health/liveness` |

---

## What NOT To Do

- ❌ Do not run Docker in production — use nssm or IIS HttpPlatformHandler
- ❌ Do not use `npm run dev` in production — always `npm run build` + IIS static serving
- ❌ Do not commit `.env.prod`, `mcp.json`, or any `sk_live_*` key to git
- ❌ Do not skip `readiness_proofs.py` before go-live
