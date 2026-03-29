import unittest
import requests
import os
import sys
import time

sys.path.append(os.getcwd())

class SovereignIntegrityAudit(unittest.TestCase):
    BASE_URL = "https://api.realms2riches.com"
    NGROK_URL = "https://api.realms2riches.com"

    def test_01_health_and_rag_count(self):
        """Verify API Health and non-zero RAG vector count."""
        print("\n[AUDIT] Checking Neural Heartbeat & RAG State...")
        try:
            res = requests.get(f"{self.BASE_URL}/health", timeout=5)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "ok")
            self.assertIn("rag", data)
            self.assertGreater(data["rag"], 0, "RAG vectors are reporting 0. Potential indexing failure.")
            print(f"✅ RAG VERIFIED: {data['rag']} vectors online.")
        except Exception as e:
            self.fail(f"Health Audit Failed: {e}")

    def test_02_product_serialization(self):
        """Verify catalog returns valid, priced products."""
        print("[AUDIT] Verifying Product Catalog Integrity...")
        try:
            res = requests.get(f"{self.BASE_URL}/products", timeout=5)
            self.assertEqual(res.status_code, 200)
            products = res.json()
            self.assertGreater(len(products), 0)
            for p in products:
                self.assertIn("name", p)
                price = p.get("price") or (p.get("prices") and p["prices"][0].get("price"))
                self.assertIsNotNone(price, f"Product {p.get('name')} has no price.")
            print(f"✅ CATALOG VERIFIED: {len(products)} products ready for sale.")
        except Exception as e:
            self.fail(f"Catalog Audit Failed: {e}")

    def test_03_lead_capture_flow(self):
        """Test lead capture funnel and guide delivery."""
        print("[AUDIT] Verifying Acquisition Funnel...")
        payload = {"email": "audit_v4@sovereign.ai", "source": "wizard_audit"}
        try:
            res = requests.post(f"{self.BASE_URL}/api/leads", json=payload, timeout=5)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertIn("guide_url", data)
            self.assertTrue(data["guide_url"].endswith(".txt"))
            print(f"✅ FUNNEL VERIFIED: Guide accessible at {data['guide_url']}")
        except Exception as e:
            self.fail(f"Lead Capture Audit Failed: {e}")

    def test_04_live_dispatch_and_meta_audit(self):
        """TRIGGER LIVE DISPATCH AND AUDIT META CONTENT."""
        print("[AUDIT] Triggering Live social Dispatch...")
        try:
            dispatch = requests.post(f"{self.BASE_URL}/api/admin/test-dispatch", timeout=35)
            self.assertEqual(dispatch.status_code, 200)
            
            print("[AUDIT] Fetching last post from Meta for Verification...")
            time.sleep(5) # Propagation wait
            audit = requests.get(f"{self.BASE_URL}/api/admin/audit-last-post", timeout=10)
            self.assertEqual(audit.status_code, 200)
            fb_data = audit.json().get("facebook", {})
            
            self.assertEqual(fb_data.get("status"), "verified", f"FB Post Incomplete: {fb_data.get('reason')}")
            self.assertTrue(fb_data.get("has_monetization"), "Last post lacks Stripe link.")
            self.assertTrue(fb_data.get("has_image"), "Last post lacks Visual Asset.")
            print("✅ DISPATCH VERIFIED: Asset and Monetization link detected live on Meta.")
        except Exception as e:
            self.fail(f"Social Audit Failed: {e}")

if __name__ == "__main__":
    print("\n👑 SOVEREIGN GRAND WIZARD MASTER AUDIT v4.1 👑")
    unittest.main()

