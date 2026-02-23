import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntegrityTest")

BASE_URL = "https://glowfly-sizeable-lazaro.ngrok-free.dev"

def test_pipeline():
    logger.info("--- INITIATING SYSTEM INTEGRITY AUDIT ---")
    
    # 1. Health
    try:
        res = requests.get(f"{BASE_URL}/health")
        logger.info(f"✅ Health Check: {res.json().get('status')} (v{res.json().get('version')})")
    except: logger.error("❌ Health Check: FAILED")

    # 2. Products
    try:
        res = requests.get(f"{BASE_URL}/products")
        logger.info(f"✅ Product Catalog: {len(res.json())} items active.")
    except: logger.error("❌ Product Catalog: FAILED")

    # 3. Dispatch
    logger.info("🚀 Triggering LIVE Manual Dispatch...")
    try:
        res = requests.post(f"{BASE_URL}/api/admin/test-dispatch")
        data = res.json()
        logger.info(f"Dispatch Result: {data.get('status')}")
        logger.info(f"Channel Detailed Metrics: {json.dumps(data.get('results'), indent=2)}")
        
        fb = data.get("results", {}).get("facebook")
        if fb == "success":
            logger.info("💎 FACEBOOK BUY BUTTON: VERIFIED ONLINE")
        else:
            logger.warning(f"⚠️ FACEBOOK STATE: {fb}")
            
    except Exception as e:
        logger.error(f"❌ Dispatch Test: EXCEPTION - {e}")

if __name__ == "__main__":
    test_pipeline()
