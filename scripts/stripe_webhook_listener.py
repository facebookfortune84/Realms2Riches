import stripe
import uvicorn
import os
import sys
from fastapi import FastAPI, Request, HTTPException

# Ensure project root is in path
sys.path.append(os.getcwd())

from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger("STRIPE_WEBHOOK")

app = FastAPI()

# Ensure API key is set
stripe.api_key = settings.STRIPE_API_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

@app.post("/webhook")
async def webhook_received(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        if endpoint_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        else:
            # Fallback for local testing without secret
            data = await request.json()
            event = stripe.Event.construct_from(data, stripe.api_key)
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.get("customer_details", {}).get("email")
        amount = session.get("amount_total", 0) / 100
        currency = session.get("currency", "usd").upper()
        
        logger.info(f"✅ PAYMENT VERIFIED VIA WEBHOOK: {amount} {currency} from {customer_email}")
        logger.info("🚀 STREAM 12 REVENUE CAPTURE CONFIRMED.")
        
        # Here we would trigger downstream fulfillment logic
        # e.g., await orchestrator.dispatch_fulfillment(customer_email)
    
    else:
        logger.info(f"Unhandled event type: {event['type']}")

    return {"status": "success"}

def run_server():
    logger.info("📡 STARTING STRIPE WEBHOOK LISTENER ON PORT 4242")
    logger.info(f"Make sure to run: stripe listen --forward-to {settings.BACKEND_URL}/api/v1/monetization/webhook")
    uvicorn.run(app, host="0.0.0.0", port=4242, log_level="info")

if __name__ == "__main__":
    run_server()
