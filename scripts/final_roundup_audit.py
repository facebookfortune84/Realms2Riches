import os
import json
import requests
import unittest
import sys
import time

sys.path.append(os.getcwd())

class SovereignFinalAudit(unittest.TestCase):
    BASE_URL = "http://localhost:8000"

    def setUp(self):
        print("   -> Polling for Matrix Readiness (5 min max)...")
        for i in range(60):
            try:
                res = requests.get(f"{self.BASE_URL}/health", timeout=5)
                if res.status_code == 200 and res.json().get("status") == "ok":
                    print(f"   -> Matrix Online (Ready at {i*5}s).")
                    return
            except: pass
            time.sleep(5)
        self.fail("Orchestrator failed to initialize in time.")

    def test_01_core(self):
        print("\n[AUDIT] 1. Core...")
        res = requests.get(f"{self.BASE_URL}/health")
        self.assertEqual(res.status_code, 200)
        print("✅ PASS")

    def test_02_revenue(self):
        print("[AUDIT] 2. Revenue...")
        res = requests.get(f"{self.BASE_URL}/products")
        self.assertGreater(len(res.json()), 0)
        print("✅ PASS")

    def test_03_social(self):
        print("[AUDIT] 3. Social...")
        # We always trigger fresh to verify LLM + API track
        print("   -> Triggering fresh dispatch (120s timeout)...")
        res = requests.post(f"{self.BASE_URL}/api/admin/test-dispatch", timeout=120)
        self.assertEqual(res.status_code, 200)
        
        print("   -> Waiting 20s for Meta propagation...")
        time.sleep(20)
        
        res = requests.get(f"{self.BASE_URL}/api/admin/audit-last-post", timeout=20)
        fb = res.json().get("facebook", {})
        self.assertEqual(fb.get("status"), "verified", f"Social Incomplete: {fb.get('reason')}")
        print("✅ PASS: Social monetization verified live.")

    def test_04_workforce(self):
        print("[AUDIT] 4. Workforce...")
        res = requests.get(f"{self.BASE_URL}/api/workforce/role-call")
        self.assertEqual(res.status_code, 200)
        print(f"✅ PASS: Agents online and introduced.")

if __name__ == "__main__":
    print("\n👑 SOVEREIGN MASTER AUDIT v5.6 👑")
    unittest.main()
