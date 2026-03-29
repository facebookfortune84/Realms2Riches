import pytest
import os
import json
import subprocess
import sys
from datetime import datetime

# Setup paths for secondary core
current_dir = os.path.dirname(os.path.abspath(__file__))
core_secondary_root = os.path.dirname(os.path.dirname(current_dir))
# Ensure secondary core is searched BEFORE the main root
if core_secondary_root not in sys.path:
    sys.path.insert(0, core_secondary_root)

from orchestrator.src.core.config import settings
from orchestrator.src.tools.db_health import check_db_health
from orchestrator.src.tools.marketing_check import check_marketing_readiness
from orchestrator.src.core.catalog.api import catalog_api

REPORT_PATH = "data/lineage/launch_readiness_report.json"

def run_pytest(args):
    """Run pytest programmatically and return exit code."""
    # Pass -c /dev/null to avoid root pyproject.toml interference, 
    # or pass the secondary one.
    config_path = os.path.join(core_secondary_root, "pyproject.toml")
    if os.path.exists(config_path):
        args = ["-c", config_path] + args
    return pytest.main(args)

def test_launch_readiness():
    print("\n--- LAUNCH READINESS META-TEST (SECONDARY) ---\n")
    
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "pending",
        "checks": {}
    }

    # 1. Environment & Config
    print("[1/6] Checking Configuration...")
    missing_vars = []
    required_vars = ["GROQ_API_KEY", "BRAND_NAME"]
    if settings.VOICE_ENABLED:
        required_vars.extend(["STT_PROVIDER", "TTS_PROVIDER"])
    
    for var in required_vars:
        val = getattr(settings, var, None)
        if not val or "placeholder" in str(val).lower() or "dummy" in str(val).lower():
            if var == "GROQ_API_KEY" and os.environ.get("GROQ_API_KEY") == "dummy":
                pass 
            else:
                missing_vars.append(var)
    
    report["checks"]["config"] = {
        "status": "pass" if not missing_vars else "fail",
        "missing": missing_vars
    }
    if missing_vars:
        print(f"❌ Config Check Failed: Missing {missing_vars}")
    else:
        print("✅ Config Check Passed")

    # 2. Database Connectivity
    print("[2/6] Checking Database...")
    db_ok = check_db_health()
    report["checks"]["database"] = {"status": "pass" if db_ok else "fail"}
    if db_ok:
        print("✅ Database Reachable")
    else:
        print("❌ Database Check Failed")

    # 3. Product Catalog
    print("[3/6] Checking Product Catalog...")
    products = catalog_api.get_products()
    catalog_ok = len(products) > 0
    report["checks"]["catalog"] = {
        "status": "pass" if catalog_ok else "fail",
        "count": len(products)
    }
    if catalog_ok:
        print(f"✅ Catalog Seeded ({len(products)} products found)")
    else:
        print("❌ Catalog Empty")

    # 4. Marketing Readiness
    print("[4/6] Checking Marketing Assets...")
    marketing_ok = check_marketing_readiness()
    report["checks"]["marketing"] = {"status": "pass" if marketing_ok else "fail"}
    if marketing_ok:
        print("✅ Marketing Config Valid")
    else:
        print("⚠️ Marketing Config uses placeholders")

    # 5. Run Test Suite
    print("[5/6] Running System Tests (Unit/Integration/E2E)...")
    tests_root = os.path.dirname(current_dir)
    
    test_files = [
        os.path.join(tests_root, "e2e", "test_full_flow.py"),
        os.path.join(tests_root, "e2e", "test_marketing_ready_flow.py"),
        os.path.join(tests_root, "integration", "test_voice_flow.py")
    ]
    
    test_files = [f for f in test_files if os.path.exists(f)]
    
    # Also add the root to sys.path for the inner pytest process
    # But pytest.main runs in the same process.
    exit_code = run_pytest(test_files)
    tests_ok = (exit_code == 0)
    report["checks"]["tests"] = {"status": "pass" if tests_ok else "fail", "exit_code": exit_code}
    
    if tests_ok:
        print("✅ All System Tests Passed")
    else:
        print("❌ System Tests Failed")

    # 6. Governance & Versioning
    print("[6/6] Checking Governance...")
    try:
        git_tag = subprocess.check_output(["git", "describe", "--tags"], stderr=subprocess.DEVNULL).decode().strip()
    except:
        git_tag = "no-tag"
    
    report["checks"]["governance"] = {
        "git_tag": git_tag,
        "lineage_manifest": os.path.exists("data/lineage/launch_manifest.json")
    }
    print(f"ℹ️ Git Tag: {git_tag}")

    overall_status = "READY" if (not missing_vars and db_ok and catalog_ok and tests_ok and marketing_ok) else "NOT READY"
    report["status"] = overall_status
    
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"\n--- OVERALL STATUS: {overall_status} ---")
    
    if overall_status != "READY":
        pytest.fail("Launch Readiness Check Failed")

if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
