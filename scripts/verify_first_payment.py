import stripe
import sys
import os
import time
from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger("STRIPE_VERIFIER")

stripe.api_key = settings.STRIPE_API_KEY

def verify_payment_flow():
    logger.info("💸 MONITORING STRIPE FOR FIRST PAYMENT 💸")
    
    if not settings.STRIPE_API_KEY:
        logger.error("❌ STRIPE_API_KEY IS MISSING.")
        sys.exit(1)

    try:
        # Check for recent events
        # We look for checkout.session.completed as it's our primary conversion event
        events = stripe.Event.list(limit=5, type="checkout.session.completed")
        
        if not events.data:
            logger.info("⏳ No payments detected yet. The autonomous engine is still spinning...")
            return False
            
        for event in events.data:
            session = event.data.object
            customer_email = session.get("customer_details", {}).get("email")
            amount = session.get("amount_total") / 100
            currency = session.get("currency").upper()
            
            logger.info(f"✅ VERIFIED PAYMENT: {amount} {currency} from {customer_email}")
            logger.info(f"🚀 MISSION CRITICAL SUCCESS: FIRST PAYMENT CAPTURED.")
            return True
            
    except Exception as e:
        logger.error(f"❌ Stripe verification failed: {e}")
        return False

if __name__ == "__main__":
    success = verify_payment_flow()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
