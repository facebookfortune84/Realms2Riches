import unittest
import requests
import json
import os
import sys
import time

sys.path.append(os.getcwd())

class TestSovereignSystem(unittest.TestCase):
    BASE_URL = "http://localhost:8000"
    NGROK_URL = "https://glowfly-sizeable-lazaro.ngrok-free.dev"

    def setUp(self):
        # Wait for API to be ready if needed
        pass

    def test_01_api_health(self):
        """Verify the API is online and reporting active agents."""
        print("
[TEST] Checking Health...")
        try:
            res = requests.get(f"{self.BASE_URL}/health", timeout=5)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "ok")
            self.assertGreater(data["agents"], 0)
            print(f"✅ Health OK: {data['agents']} Agents Active.")
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
        res = requests.post(f"{self.BASE_URL}/api/leads", json=payload, timeout=5)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        self.assertIn("guide_url", data)
        self.assertIn(self.NGROK_URL, data["guide_url"])
        print(f"✅ Lead Capture OK: Asset URL -> {data['guide_url']}")

    def test_04_social_dispatch_simulation(self):
        """Trigger a manual social dispatch and verify structure."""
        print("[TEST] Triggering Manual Social Dispatch...")
        # Note: This hits the actual Facebook API if keys are live. 
        # We verify the backend handles the request correctly.
        res = requests.post(f"{self.BASE_URL}/api/admin/test-dispatch", timeout=30)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        self.assertEqual(data["status"], "success")
        print("✅ Dispatch OK: System reported success.")
        if "dispatch_results" in data:
            print(f"   Results: {json.dumps(data['dispatch_results'], indent=2)}")

    def test_05_opt_out_compliance(self):
        """Verify the opt-out endpoint works."""
        print("[TEST] Checking Opt-Out Endpoint...")
        res = requests.get(f"{self.BASE_URL}/api/user/opt-out?email=leave@me.alone")
        self.assertEqual(res.status_code, 200)
        self.assertIn("unsubscribed", res.json()["message"])
        print("✅ Opt-Out OK.")

if __name__ == "__main__":
    print("🦅 STARTING COMPREHENSIVE SOVEREIGN SYSTEM AUDIT 🦅")
    unittest.main()
