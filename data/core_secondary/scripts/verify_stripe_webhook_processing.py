import time
import requests
import json
import hmac
import hashlib
import os
import sys

# Ensure the project root is in the path for 'orchestrator' imports
sys.path.append(os.getcwd())

from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger("WEBHOOK_VERIFIER")

def generate_stripe_signature(payload_str, secret):
    timestamp = int(time.time())
    signed_payload = f"{timestamp}.{payload_str}"
    signature = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={signature}"

def test_webhook():
    logger.info("💸 STARTING STRIPE WEBHOOK LOGIC VERIFICATION 💸")
    
    # Check if secret is set
    secret = settings.STRIPE_WEBHOOK_SECRET
    if not secret or secret == "placeholder":
        logger.warning("⚠️ STRIPE_WEBHOOK_SECRET is missing. The listener will use fallback mode (no signature check).")
        # In fallback mode, we don't need a signature, but the listener expects one if it checks headers.
    
    payload = {
        "id": "evt_test_v5",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_v5",
                "customer_details": {
                    "email": "customer_v5@example.com"
                },
                "amount_total": 299900,
                "currency": "usd",
                "payment_status": "paid"
            }
        }
    }
    
    payload_str = json.dumps(payload)
    
    headers = {"Content-Type": "application/json"}
    if secret and secret != "placeholder":
        sig = generate_stripe_signature(payload_str, secret)
        headers["stripe-signature"] = sig
        logger.info("✅ Generated valid Stripe signature.")
    
    # Attempt to ping the listener
    # Note: Port 4242 is specified in scripts/stripe_webhook_listener.py for local execution
    # But we use the live ngrok URL for the primary verification
    url = f"{settings.BACKEND_URL}/api/v1/monetization/webhook"
    
    headers[""] = "true"
    headers["x-sovereign-internal"] = "true"
    
    # Fallback removed - Strict Production Verification
    # if "localhost" in url and os.name == "nt":
    #     url = "http://localhost:4242/webhook"
    
    logger.info(f"🚀 Dispatching simulated payment to {url}...")
    
    try:
        response = requests.post(url, data=payload_str, headers=headers, timeout=5)
        
        if response.status_code == 200:
            logger.info("✅ SUCCESS: Webhook listener processed the payload correctly.")
            logger.info(f"   Response: {response.json()}")
            return True
        else:
            logger.error(f"❌ FAILED: Listener returned status code {response.status_code}")
            logger.error(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ FAILED: Could not connect to the webhook listener.")
        logger.error("   Ensure the listener is running: python scripts/stripe_webhook_listener.py")
        return False
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_webhook()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

