import requests
import json
import time

BASE_URL = "https://api.realms2riches.com"

def audit_endpoints():
    print("💎 STARTING COMPREHENSIVE API AUDIT 💎")
    print("========================================")
    
    endpoints = [
        {"method": "GET", "path": "/health"},
        {"method": "GET", "path": "/api/integrations/status"},
        {"method": "GET", "path": "/api/telemetry/stats"},
        {"method": "GET", "path": "/api/activity"},
        {"method": "GET", "path": "/products"},
        {"method": "POST", "path": "/api/leads", "body": {"email": "audit@sovereign.ai", "source": "audit"}},
        {"method": "POST", "path": "/api/checkout/session", "body": {"priceId": "price_titan_pro", "email": "king@commerce.com"}},
    ]
    
    results = []
    
    for ep in endpoints:
        method = ep["method"]
        path = ep["path"]
        url = f"{BASE_URL}{path}"
        print(f"Testing {method} {path}...")
        
        try:
            if method == "GET":
                res = requests.get(url, timeout=10)
            else:
                res = requests.post(url, json=ep.get("body", {}), timeout=10)
            
            status = "✅ PASS" if res.status_code < 400 else f"❌ FAIL ({res.status_code})"
            results.append({"endpoint": path, "status": status, "code": res.status_code})
            print(f"   Status: {status}")
            if res.status_code >= 400:
                print(f"   Response: {res.text[:200]}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append({"endpoint": path, "status": "❌ ERROR", "reason": str(e)})

    print("\n📊 AUDIT SUMMARY")
    print("========================================")
    for r in results:
        print(f"{r['endpoint']:<30} | {r['status']}")

if __name__ == "__main__":
    audit_endpoints()

