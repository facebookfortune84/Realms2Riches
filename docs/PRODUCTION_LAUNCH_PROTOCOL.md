# Realms2Riches - PRODUCTION LAUNCH PROTOCOL (v5.8.0)

This document defines the immutable sequence for a production-grade launch of the Sovereign Matrix.

## 🛡️ Pre-Launch Verification
Before executing the launch, ensure the `readiness_proofs.py` returns **100% SUCCESS**.

```powershell
python scripts/readiness_proofs.py
```

## 🚀 Step 1: Industrial Launch Sequence
Run the primary launch commander. This will perform smart Docker rebuilds (only if necessary), verify system integrity, and unleash the swarm.

```powershell
.\SOVEREIGN_START.ps1
```

### Options:
- `-Prune`: Force a clean rebuild of all containers and volumes (Destructive).
- `-SkipTests`: Skip pre-launch integrity audits (Not recommended for Production).

## 📡 Step 2: Connectivity & Gateway
The system defaults to your production Ngrok gateway:
- **Backend API:** `https://glowfly-sizeable-lazaro.ngrok-free.dev`
- **Frontend UI:** `https://frontend-two-xi-gal9lkptfi.vercel.app/`

Ensure your Ngrok tunnel is authenticated and using the static domain assigned to your account.

## 💰 Step 3: Monetization Handshake
Once the system is live, verify the Stripe webhook loop:

```powershell
python scripts/verify_stripe_webhook_processing.py
```

Then, monitor for the first live payment:

```powershell
python scripts/verify_first_payment.py
```

## 🔐 Step 4: Lineage Lock & Finality
After a successful launch, lock the cryptographic state and tag the repository.

```powershell
# Lock Lineage (Generates daily integrity manifest)
python infra/scripts/hash_registry.py

# Final Sovereign Commit
git add .
git commit -m "🚀 PRODUCTION LAUNCH v5.8.0 | [13 Streams Active]"
git tag -a v5.8.0 -m "Realms2Riches Production Release v5.8.0"
git push origin dev --tags
```

## 📊 Step 5: Live Monitoring
- **Swarm Transparency:** `https://glowfly-sizeable-lazaro.ngrok-free.dev/api/v1/swarm/transparency`
- **Profit Dashboard:** `python scripts/profit_dashboard.py`
- **Container Logs:** `docker-compose -f infra/docker/docker-compose.prod.yml logs -f`

---
**Watch the money move. Launch sequence complete.**
