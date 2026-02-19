import requests
import os
import sys

def check_backend():
    # Allow overriding URL via env var, default to local if not set, or read from .env.prod if needed
    # For CI/CLI context where .env.prod might be loaded or we just want to hit localhost
    url = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # If running from outside container against localhost
    print(f"Probing Backend at: {url}")
    
    try:
        resp = requests.get(f"{url}/health", timeout=5)
        print(f"Status Code: {resp.status_code}")
        print(f"Response Body: {resp.text}")
        
        if resp.status_code == 200:
            print("✅ Backend Health Check PASSED")
            sys.exit(0)
        else:
            print("❌ Backend Health Check FAILED (Non-200)")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Backend Health Check FAILED (Connection Error): {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_backend()
