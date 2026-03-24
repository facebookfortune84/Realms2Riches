import requests
import json
import uuid
import time
from datetime import datetime

WEBHOOK_URL = "http://localhost:8000/api/v1/monetization/webhook"

def generate_mock_event():
    """Generates a sovereign checkout.session.completed event."""
    session_id = f"cs_test_{uuid.uuid4()}"
    return {
        "id": f"evt_{uuid.uuid4()}",
        "object": "event",
        "api_version": "2023-10-16",
        "created": int(time.time()),
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": session_id,
                "object": "checkout.session",
                "amount_total": 9900, # $99.00
                "currency": "usd",
                "customer_details": {
                    "email": "robert.demotto@realms2riches.com",
                    "name": "Robert DeMotto"
                },
                "metadata": {
                    "product_id": "stream_12_access",
                    "affiliate_code": "SOVEREIGN_V1"
                },
                "payment_status": "paid",
                "status": "complete"
            }
        }
    }

def main():
    print("💰 SOVEREIGN MONETIZATION VERIFICATION")
    print("======================================")
    print(f"Target: {WEBHOOK_URL}")
    
    payload = generate_mock_event()
    headers = {
        "Content-Type": "application/json",
        "x-sovereign-internal": "true" # Bypass signature verification for internal testing
    }
    
    print(f"\n🚀 Dispatching Mock Webhook Event: {payload['type']}")
    print(f"Details: {payload['data']['object']['amount_total']} cents, User: {payload['data']['object']['customer_details']['email']}")
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=5)
        
        if response.status_code == 200:
            print(f"\n✅ SUCCESS: Webhook accepted. (Status: {response.status_code})")
            print(f"Response: {response.json()}")
        else:
            print(f"\n❌ FAILURE: Webhook rejected. (Status: {response.status_code})")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR: Could not connect to the webhook listener.")
        print("Ensure the server is running: 'python scripts/stripe_webhook_listener.py' or 'uvicorn ...'")

if __name__ == "__main__":
    main()
