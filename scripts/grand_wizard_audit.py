import asyncio
import requests
import json
import os
import sys
import time
from typing import Dict, Any

# Ensure project root is in path
sys.path.append(os.getcwd())

class GrandWizardAudit:
    """
    Extensive, no-hallucination project audit suite.
    Verifies every track, endpoint, and data integrity point.
    """
    BASE_URL = "http://localhost:8000"
    FRONTEND_URL = "https://frontend-two-xi-gal9lkptfi.vercel.app/"
    NGROK_URL = "https://glowfly-sizeable-lazaro.ngrok-free.dev"

    def __init__(self):
        self.results = {}

    def log_result(self, name: str, success: bool, details: Any):
        status = "✅ PASS" if success else "❌ FAIL"
        self.results[name] = {"success": success, "details": details}
        print(f"{status} | {name}: {details}")

    async def run_all(self):
        print("
🧙‍♂️ STARTING GRAND WIZARD MASTER AUDIT v4.2 🧙‍♂️
")
        
        # 1. API Pulse & RAG Integrity
        try:
            res = requests.get(f"{self.BASE_URL}/health", timeout=5)
            data = res.json()
            rag_count = data.get("rag", 0)
            self.log_result("API_HEALTH", res.status_code == 200, f"Status: {data.get('status')} | Version: {data.get('version')}")
            self.log_result("RAG_INTEGRITY", rag_count > 0, f"Vector Count: {rag_count}")
        except Exception as e:
            self.log_result("API_HEALTH", False, str(e))

        # 2. Revenue Matrix (Catalog)
        try:
            res = requests.get(f"{self.BASE_URL}/products", timeout=5)
            products = res.json()
            platinum = next((p for p in products if "Platinum" in p.get("name", "")), None)
            price = 0
            if platinum:
                price = platinum.get("price") or (platinum.get("prices") and platinum["prices"][0].get("price"))
            self.log_result("REVENUE_CATALOG", len(products) > 0 and price == 2999.0, f"Products: {len(products)} | Platinum: ${price}")
        except Exception as e:
            self.log_result("REVENUE_CATALOG", False, str(e))

        # 3. Acquisition Funnel (Leads)
        try:
            payload = {"email": "wizard@sovereign.ai", "source": "grand_audit"}
            res = requests.post(f"{self.BASE_URL}/api/leads", json=payload, timeout=10)
            data = res.json()
            guide_url = data.get("guide_url", "")
            
            # Verify asset actually exists and is served
            asset_res = requests.get(guide_url, timeout=5)
            self.log_result("LEAD_CAPTURE", res.status_code == 200, f"Lead recorded. Guide: {guide_url}")
            self.log_result("ASSET_SERVING", asset_res.status_code == 200, f"Guide download verified ({len(asset_res.text)} bytes)")
        except Exception as e:
            self.log_result("LEAD_CAPTURE", False, str(e))

        # 4. Social Dispatch & Monetization Audit
        try:
            # Trigger fresh dispatch
            requests.post(f"{self.BASE_URL}/api/admin/test-dispatch", timeout=40)
            print("   ...waiting for Meta propagation (5s)...")
            time.sleep(5)
            
            # Audit the post live from Meta
            res = requests.get(f"{self.BASE_URL}/api/admin/audit-last-post", timeout=15)
            audit = res.json().get("facebook", {})
            verified = audit.get("status") == "verified"
            self.log_result("SOCIAL_MONETIZATION", verified, f"FB Verified: {verified} | Link: {audit.get('has_monetization')} | Image: {audit.get('has_image')}")
        except Exception as e:
            self.log_result("SOCIAL_MONETIZATION", False, str(e))

        # 5. Genesis Forge (Project Scaffolding)
        try:
            task = "INITIALIZE COMPANY BLUEPRINT: Name: Audit Corp, Industry: Defense."
            res = requests.post(f"{self.BASE_URL}/api/tasks", json={"description": task}, timeout=60)
            self.log_result("GENESIS_FORGE", res.status_code == 200 and res.json().get("status") == "completed", "Project track verified.")
        except Exception as e:
            self.log_result("GENESIS_FORGE", False, str(e))

        # 6. Compliance & Opt-Out
        try:
            res = requests.get(f"{self.BASE_URL}/api/user/opt-out?email=audit@sovereign.ai")
            self.log_result("COMPLIANCE_GDPR", res.status_code == 200, "User opt-out path verified.")
        except Exception as e:
            self.log_result("COMPLIANCE_GDPR", False, str(e))

        # Summary
        total = len(self.results)
        passed = sum(1 for r in self.results.values() if r["success"])
        print(f"
📊 AUDIT SUMMARY: {passed}/{total} Tracks Online.")
        
        if passed == total:
            print("
✅ SYSTEM ALIGNED. READY FOR EXPANSION.")
            return True
        else:
            print("
❌ SYSTEM DEVIATED. Repairs required.")
            return False

if __name__ == "__main__":
    audit = GrandWizardAudit()
    success = asyncio.run(audit.run_all())
    if not success: sys.exit(1)
