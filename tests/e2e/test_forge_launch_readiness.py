import pytest
import os
import json
import subprocess
import sys
from datetime import datetime
from orchestrator.src.core.config import settings
from orchestrator.src.tools.db_health import check_db_health
from orchestrator.src.core.catalog.api import catalog_api
from orchestrator.src.core.api import app
from fastapi.testclient import TestClient

REPORT_PATH = "data/lineage/launch_readiness_report.json"
client = TestClient(app)

def test_forge_launch_readiness():
    print("
--- FORGE LAUNCH READINESS META-TEST ---
")
    
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "pending",
        "checks": {}
    }

    # 1. Backend Health
    print("[1/7] Checking Backend API...")
    resp = client.get("/health")
    backend_ok = (resp.status_code == 200)
    report["checks"]["backend"] = "pass" if backend_ok else "fail"
    if backend_ok:
        print("✅ Backend Health OK")
    else:
        print(f"❌ Backend Health Failed: {resp.status_code}")

    # 2. Database & Catalog
    print("[2/7] Checking DB & Catalog...")
    db_ok = check_db_health()
    products = catalog_api.get_products()
    catalog_ok = len(products) > 0
    report["checks"]["database"] = "pass" if db_ok else "fail"
    report["checks"]["catalog"] = "pass" if catalog_ok else "fail"
    
    if db_ok: print("✅ DB Connection OK")
    else: print("❌ DB Connection Failed")
    
    if catalog_ok: print(f"✅ Catalog OK ({len(products)} items)")
    else: print("❌ Catalog Empty")

    # 3. Stripe Config
    print("[3/7] Checking Stripe Config...")
    stripe_ok = bool(settings.STRIPE_API_KEY and settings.STRIPE_API_KEY != "placeholder")
    report["checks"]["stripe"] = "pass" if stripe_ok else "warn" # Warn if not set, might be intentional for some
    if stripe_ok: print("✅ Stripe Key Configured")
    else: print("⚠️ Stripe Key Missing/Placeholder")

    # 4. Voice Config
    print("[4/7] Checking Voice Config...")
    voice_ok = settings.VOICE_ENABLED
    report["checks"]["voice"] = "pass" if voice_ok else "info"
    if voice_ok: print("✅ Voice Enabled")
    else: print("ℹ️ Voice Disabled in Config")

    # 5. Agent Swarm
    print("[5/7] Checking Agent Swarm...")
    resp = client.get("/api/agents/health")
    agents_health = resp.json()
    all_agents_ok = all(status == "OK" for status in agents_health.values()) and len(agents_health) > 0
    report["checks"]["agents"] = "pass" if all_agents_ok else "fail"
    
    print("Agent Status:")
    for aid, status in agents_health.items():
        print(f"  - {aid}: {status}")
        
    if all_agents_ok: print("✅ All Agents Healthy")
    else: print("❌ Some Agents Unhealthy or None Found")

    # 6. Cockpit Task Flow (Mock)
    print("[6/7] Testing Cockpit Task Flow...")
    task_payload = {"description": "Test task from launch check"}
    resp = client.post("/api/tasks", json=task_payload)
    task_ok = (resp.status_code == 200)
    report["checks"]["task_flow"] = "pass" if task_ok else "fail"
    if task_ok: print("✅ Task Submission OK")
    else: print(f"❌ Task Submission Failed: {resp.status_code}")

    # 7. Metrics
    print("[7/7] Checking Metrics...")
    resp = client.get("/metrics")
    metrics_ok = (resp.status_code == 200)
    report["checks"]["metrics"] = "pass" if metrics_ok else "fail"
    if metrics_ok: print("✅ Metrics Endpoint OK")
    else: print("❌ Metrics Endpoint Failed")

    # Final Summary
    overall_status = "READY" if (backend_ok and db_ok and catalog_ok and all_agents_ok and task_ok) else "NOT READY"
    report["status"] = overall_status
    
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"
--- FINAL STATUS: {overall_status} ---")
    
    if overall_status != "READY":
        pytest.fail("Forge Launch Readiness Check Failed")

if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
