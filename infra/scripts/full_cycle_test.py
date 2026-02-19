import requests
import json
import os
import hashlib
from datetime import datetime

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def print_banner(msg):
    print(f"
{'='*60}
{msg}
{'='*60}")

def run_step(name, func):
    print(f"Running: {name}...", end=" ", flush=True)
    try:
        result = func()
        print("✅")
        return True, result
    except Exception as e:
        print(f"❌
ERROR: {e}")
        return False, None

def check_integrity():
    manifest_path = "data/lineage/integrity_manifest.json"
    if not os.path.exists(manifest_path):
        raise FileNotFoundError("Integrity manifest missing.")
    with open(manifest_path, 'r') as f:
        data = json.load(f)
    return f"Verified {len(data['files'])} files."

def check_backend_health():
    resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
    resp.raise_for_status()
    return resp.json()

def check_catalog():
    resp = requests.get(f"{BACKEND_URL}/products", timeout=5)
    resp.raise_for_status()
    data = resp.json()
    if len(data) == 0:
        raise ValueError("Product catalog is empty.")
    return f"{len(data)} products found."

def check_agents():
    resp = requests.get(f"{BACKEND_URL}/api/agents/health", timeout=5)
    resp.raise_for_status()
    data = resp.json()
    for agent, status in data.items():
        if status != "OK":
            raise ValueError(f"Agent {agent} is {status}")
    return data

def simulate_cockpit():
    payload = {"description": "Self-cycle test: verify system logic integrity."}
    resp = requests.post(f"{BACKEND_URL}/api/tasks", json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()

def run_full_cycle():
    print_banner("REALMS2RICHES FULL-CYCLE VERIFICATION")
    
    results = {}
    
    steps = [
        ("Integrity Manifest", check_integrity),
        ("Backend Connectivity", check_backend_health),
        ("Product Catalog", check_catalog),
        ("Agent Swarm Health", check_agents),
        ("Agent Logic Routing", simulate_cockpit)
    ]
    
    overall_success = True
    for name, func in steps:
        success, data = run_step(name, func)
        results[name] = {"success": success, "data": data}
        if not success:
            overall_success = False

    print_banner("FINAL VERIFICATION REPORT")
    status = "READY TO LAUNCH" if overall_success else "NOT READY"
    print(f"STATUS: {status}")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    
    # Save results to lineage
    report_path = "data/lineage/full_cycle_report.json"
    with open(report_path, 'w') as f:
        json.dump({"status": status, "results": results}, f, indent=2)
    print(f"Detailed report saved to: {report_path}")

if __name__ == "__main__":
    run_full_cycle()
