import stripe
import requests
import time
import json
import hmac
import hashlib
import os
import sys

# Ensure the project root is in the path for 'orchestrator' imports
sys.path.append(os.getcwd())

from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger("PROD_VERIFIER")

stripe.api_key = settings.STRIPE_API_KEY

def generate_stripe_signature(payload_str, secret):
    timestamp = int(time.time())
    signed_payload = f"{timestamp}.{payload_str}"
    signature = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={signature}"

def verify_live_webhook_processing():
    """
    Simulates a live successful checkout session completion 
    to verify that the production backend and webhook listener are working correctly.
    """
    logger.info("💸 INITIATING PRODUCTION WEBHOOK VERIFICATION 💸")
    
    # 1. Check if we have the necessary credentials
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    backend_url = f"{settings.BACKEND_URL}/api/v1/monetization/webhook"
    
    if not webhook_secret or webhook_secret == "placeholder":
        logger.error("❌ STRIPE_WEBHOOK_SECRET is missing or set to placeholder.")
        return False
        
    # 2. Construct the Payload (Simulated checkout.session.completed)
    payload = {
        "id": f"evt_prod_verify_{int(time.time())}",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": f"cs_prod_verify_{int(time.time())}",
                "customer_details": {
                    "email": "robertdemottojr83@gmail.com" # Using user's email for the test
                },
                "amount_total": 299900, # $2,999.00
                "currency": "usd",
                "payment_status": "paid",
                "metadata": {
                    "source": "production_verification_script",
                    "stream": "Stream 12"
                }
            }
        },
        "created": int(time.time())
    }
    
    payload_str = json.dumps(payload)
    
    # 3. Generate Signature
    signature = generate_stripe_signature(payload_str, webhook_secret)
    
    headers = {
        "Content-Type": "application/json",
        "stripe-signature": signature,
        "ngrok-skip-browser-warning": "true",
        "x-sovereign-internal": "true"
    }
    
    logger.info(f"🚀 Sending simulated live event to: {backend_url}")
    
    try:
        response = requests.post(backend_url, data=payload_str, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ SUCCESS: Webhook processing verified at production endpoint.")
            logger.info(f"   Response Body: {response.text}")
            return True
        else:
            logger.error(f"❌ FAILED: Webhook returned status {response.status_code}")
            logger.error(f"   Response Body: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"💥 Webhook verification error: {e}")
        return False

if __name__ == "__main__":
    success = verify_live_webhook_processing()
    if success:
        logger.info("💎 PRODUCTION CAPABILITIES VERIFIED.")
        sys.exit(0)
    else:
        logger.error("❌ PRODUCTION VERIFICATION FAILED.")
        sys.exit(1)
