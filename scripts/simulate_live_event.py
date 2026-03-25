import requests
import time
import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

from orchestrator.src.core.config import settings

def simulate_payment():
    print("💳 SIMULATING LIVE STRIPE PAYMENT (HDRB Mode)...")
    
    # Target Live Backend for direct verification
    webhook_url = f"{settings.BACKEND_URL}/api/v1/monetization/webhook"
    
    payload = {
        "id": f"evt_sim_{int(time.time())}",
        "object": "event",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_hdrb_999",
                "amount_total": 299900,
                "currency": "usd",
                "customer_details": {
                    "email": "king@commerce.com"
                },
                "metadata": {
                    "customer_email": "king@commerce.com",
                    "product_id": "prod_jarvis_hdrb"
                }
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-sovereign-internal": "true",
        "Stripe-Signature": "t=123,v1=simulated"
    }
    
    try:
        response = requests.post(webhook_url, json=payload, headers=headers)
        if response.status_code == 200:
            print("✅ FIRST SALE CAPTURED: 200 OK")
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    simulate_payment()
