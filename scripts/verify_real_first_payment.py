import stripe
import time
import sys
import os

# Ensure the project root is in the path for 'orchestrator' imports
sys.path.append(os.getcwd())

from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger("REVENUE_VERIFIER")

stripe.api_key = settings.STRIPE_API_KEY

def poll_for_payment(timeout_seconds=300):
    """
    Polls the Stripe API for a 'checkout.session.completed' event.
    Timeouts after 5 minutes by default if no payment is detected.
    """
    logger.info(f"⏳ MONITORING STRIPE FOR FIRST PAYMENT (Timeout: {timeout_seconds}s) ⏳")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        try:
            # Check for recent successful checkout sessions
            events = stripe.Event.list(limit=5, type="checkout.session.completed")
            
            if events.data:
                for event in events.data:
                    session = event.data.object
                    customer_email = session.get("customer_details", {}).get("email")
                    amount = session.get("amount_total", 0) / 100
                    currency = session.get("currency", "usd").upper()
                    
                    logger.info("💰" * 20)
                    logger.info(f"💰   VERIFIED PAYMENT: {amount} {currency} from {customer_email}")
                    logger.info("💰   MISSION CRITICAL SUCCESS: FIRST REVENUE CAPTURED!")
                    logger.info("💰" * 20)
                    return True
            
            # Print status periodically
            elapsed = int(time.time() - start_time)
            if elapsed % 30 == 0:
                logger.info(f"   Waiting... ({elapsed}s elapsed). The autonomous engine is still spinning...")
                
            time.sleep(10)
            
        except Exception as e:
            logger.error(f"❌ Stripe polling error: {e}")
            time.sleep(20)
            
    logger.warning("🕒 Verification timed out. No payments detected yet.")
    return False

if __name__ == "__main__":
    # If a command line arg is provided, use it as timeout
    timeout = 300
    if len(sys.argv) > 1:
        try:
            timeout = int(sys.argv[1])
        except ValueError:
            pass
            
    success = poll_for_payment(timeout)
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
