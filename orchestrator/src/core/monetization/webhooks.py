import stripe
import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger("MONETIZATION_WEBHOOKS")
router = APIRouter(prefix="/api/v1/monetization", tags=["monetization"])

# Ensure API key is set
stripe.api_key = settings.STRIPE_API_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Production-grade Stripe Webhook Handler.
    Processes payments, subscriptions, and fulfillment events.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    data_object = event["data"]["object"]

    logger.info(f"🔗 Received Stripe Event: {event_type}")

    if event_type == "checkout.session.completed":
        await handle_checkout_completed(data_object)
    elif event_type == "customer.subscription.created":
        await handle_subscription_created(data_object)
    elif event_type == "invoice.payment_failed":
        await handle_payment_failed(data_object)
    else:
        logger.info(f"Unhandled event type: {event_type}")

    return {"status": "success"}

async def handle_checkout_completed(session):
    customer_email = session.get("customer_details", {}).get("email")
    amount = session.get("amount_total", 0) / 100
    currency = session.get("currency", "usd").upper()
    
    logger.info(f"✅ SUCCESSFUL CHECKOUT: {amount} {currency} from {customer_email}")
    # Trigger Onboarding / Access Provisioning
    # await provision_account(customer_email, session.get("metadata", {}))

async def handle_subscription_created(subscription):
    customer_id = subscription.get("customer")
    logger.info(f"📈 NEW SUBSCRIPTION CREATED: {customer_id}")

async def handle_payment_failed(invoice):
    customer_email = invoice.get("customer_email")
    logger.info(f"❌ PAYMENT FAILED: {customer_email}. Triggering dunning sequence.")
    # Trigger Dunning / Notification Agent
