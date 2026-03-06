import requests
import json
import time
import os
from orchestrator.src.core.config import settings

def simulate_payment():
    print("💳 SIMULATING LIVE STRIPE PAYMENT...")
    
    webhook_url = f"{settings.BACKEND_URL}/api/webhooks/stripe"
    
    # Mock Event Payload
    payload = {
        "id": f"evt_sim_{int(time.time())}",
        "object": "event",
        "api_version": "2023-10-16",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": f"cs_test_{int(time.time())}",
                "object": "checkout.session",
                "amount_total": 49900,
                "currency": "usd",
                "customer_details": {
                    "email": "simulation_user@example.com",
                    "name": "Simulated Buyer"
                },
                "payment_status": "paid",
                "status": "complete"
            }
        },
        "type": "checkout.session.completed"
    }
    
    headers = {
        "Content-Type": "application/json",
        # In a real scenario, we'd sign this, but our local dev handler accepts unsigned for testing
        "Stripe-Signature": "t=123,v1=simulated_signature" 
    }
    
    try:
        response = requests.post(webhook_url, json=payload, headers=headers)
        if response.status_code == 200:
            print("✅ PAYMENT SIMULATION SUCCESSFUL")
            print(f"   Payload sent to {webhook_url}")
            print("   Check logs for 'PAYMENT CAPTURED'")
        else:
            print(f"❌ SIMULATION FAILED: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ NETWORK ERROR: {e}")
        print("   Is the API server running on port 8000?")

if __name__ == "__main__":
    simulate_payment()
