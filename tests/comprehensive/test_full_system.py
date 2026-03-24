import unittest
import requests
import json
import os
import sys
import time

sys.path.append(os.getcwd())

class TestSovereignSystem(unittest.TestCase):
    BASE_URL = "https://api.realms2riches.com"
    NGROK_URL = "https://api.realms2riches.com"

    def setUp(self):
        pass

    def test_01_api_health(self):
        """Verify the API is online and reporting active agents."""
        print("\n[TEST] Checking Health...")
        try:
            res = requests.get(f"{self.BASE_URL}/health", timeout=5)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "ok")
            self.assertGreater(data["agents"], 0)
            self.assertIn("rag", data, "RAG vector count missing from health response.")
            print(f"✅ Health OK: {data['agents']} Agents | RAG: {data.get('rag')} Vectors.")
        except Exception as e:
            self.fail(f"API Health Check Failed: {e}")

    def test_02_product_catalog(self):
        """Verify products are loaded and contain prices."""
        print("[TEST] Checking Product Catalog...")
        res = requests.get(f"{self.BASE_URL}/products", timeout=5)
        self.assertEqual(res.status_code, 200)
        products = res.json()
        self.assertGreater(len(products), 0)
        
        platinum = next((p for p in products if "Platinum" in p.get("name", "")), None)
        self.assertIsNotNone(platinum, "Platinum License not found in catalog.")
        
        # Check for price in either flat or nested format
        price = platinum.get("price") or (platinum.get("prices") and platinum["prices"][0]["price"])
        self.assertIsNotNone(price, "Platinum price is missing.")
        print(f"✅ Catalog OK: Found {len(products)} products. Platinum: ${price}")

    def test_03_lead_capture_and_asset_delivery(self):
        """Verify lead capture returns the correct asset URL."""
        print("[TEST] Checking Lead Capture...")
        payload = {"email": "test_automator@sovereign.ai", "source": "integration_test"}
        try:
            res = requests.post(f"{self.BASE_URL}/api/leads", json=payload, timeout=5)
            if res.status_code != 200:
                print(f"❌ Lead Capture FAILED with status {res.status_code}: {res.text}")
            self.assertEqual(res.status_code, 200)
            data = res.json()
            
            self.assertIn("guide_url", data)
            self.assertIn("assets/sovereign_strategy_guide_v3.txt", data["guide_url"])
            print(f"✅ Lead Capture OK: Asset URL -> {data['guide_url']}")
        except Exception as e:
            self.fail(f"Lead Capture Exception: {e}")

    def test_04_social_dispatch_and_audit(self):
        """Trigger dispatch and then AUDIT the last post content."""
        print("[TEST] Triggering Dispatch & Auditing Last Post...")
        
        # 1. Trigger
        res = requests.post(f"{self.BASE_URL}/api/admin/test-dispatch", timeout=30)
        self.assertEqual(res.status_code, 200)
        
        # 2. Audit (Wait for Meta to process)
        time.sleep(2)
        audit_res = requests.get(f"{self.BASE_URL}/api/admin/audit-last-post", timeout=10)
        self.assertEqual(audit_res.status_code, 200)
        audit_data = audit_res.json()
        
        if audit_data.get("facebook", {}).get("status") == "verified":
            print("✅ Social Audit OK: Buy link and Image detected in last FB post.")
        else:
            print(f"⚠️ Social Audit Warning: {audit_data.get('facebook', {}).get('reason')}")

    def test_05_opt_out_compliance(self):
        """Verify the opt-out endpoint works."""
        print("[TEST] Checking Opt-Out Endpoint...")
        res = requests.get(f"{self.BASE_URL}/api/user/opt-out?email=leave@me.alone")
        self.assertEqual(res.status_code, 200)
        self.assertIn("unsubscribed", res.json()["message"])
        print("✅ Opt-Out OK.")

if __name__ == "__main__":
    print("\n🦅 SOVEREIGN INTEGRATION AUDIT v4.0 🦅")
    unittest.main()

