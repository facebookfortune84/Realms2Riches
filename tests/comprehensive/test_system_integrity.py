import unittest
import requests
import json
import os
import sys
import time

sys.path.append(os.getcwd())

class SovereignIntegrityAudit(unittest.TestCase):
    BASE_URL = "http://localhost:8000"
    NGROK_URL = "https://glowfly-sizeable-lazaro.ngrok-free.dev"

    def test_01_health_and_rag_count(self):
        """Verify API Health and non-zero RAG vector count."""
        print("
[AUDIT] Checking Neural Heartbeat & RAG State...")
        res = requests.get(f"{self.BASE_URL}/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertGreater(data["rag"], 0, "RAG vectors are reporting 0. Potential indexing failure.")
        print(f"✅ RAG VERIFIED: {data['rag']} vectors online.")

    def test_02_product_serialization(self):
        """Verify catalog returns valid, priced products."""
        print("[AUDIT] Verifying Product Catalog Integrity...")
        res = requests.get(f"{self.BASE_URL}/products")
        self.assertEqual(res.status_code, 200)
        products = res.json()
        for p in products:
            self.assertIn("name", p)
            # Support both flat and nested prices
            price = p.get("price") or (p.get("prices") and p["prices"][0]["price"])
            self.assertIsNotNone(price, f"Product {p.get('name')} has no price.")
        print(f"✅ CATALOG VERIFIED: {len(products)} products ready for sale.")

    def test_03_lead_capture_and_compliance(self):
        """Test lead capture funnel and opt-out route."""
        print("[AUDIT] Verifying Acquisition Funnel & Compliance...")
        # 1. Lead Capture
        payload = {"email": "audit@sovereign.ai", "source": "master_audit"}
        res = requests.post(f"{self.BASE_URL}/api/leads", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn("guide_url", res.json())
        
        # 2. Opt-Out
        opt_res = requests.get(f"{self.BASE_URL}/api/user/opt-out?email=audit@sovereign.ai")
        self.assertEqual(opt_res.status_code, 200)
        print("✅ FUNNEL VERIFIED: Leads captured, compliance active.")

    def test_04_live_dispatch_and_conversion_audit(self):
        """TRIGGER LIVE DISPATCH AND AUDIT META CONTENT."""
        print("[AUDIT] Triggering Live social Dispatch...")
        dispatch = requests.post(f"{self.BASE_URL}/api/admin/test-dispatch")
        self.assertEqual(dispatch.status_code, 200)
        
        print("[AUDIT] Fetching last post from Meta for Verification...")
        time.sleep(3) # Wait for propagation
        audit = requests.get(f"{self.BASE_URL}/api/admin/audit-last-post")
        self.assertEqual(audit.status_code, 200)
        fb_data = audit.json().get("facebook", {})
        
        self.assertEqual(fb_data.get("status"), "verified", f"FB Post Incomplete: {fb_data.get('reason')}")
        self.assertTrue(fb_data.get("has_monetization"), "Last post lacks Stripe link.")
        self.assertTrue(fb_data.get("has_image"), "Last post lacks Image.")
        print("✅ DISPATCH VERIFIED: Image and Clickable Link detected live on Meta.")

if __name__ == "__main__":
    print("
👑 SOVEREIGN GRAND WIZARD MASTER AUDIT 👑")
    unittest.main()
