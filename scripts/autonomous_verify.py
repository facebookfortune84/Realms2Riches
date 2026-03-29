import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
from datetime import datetime

# Ensure the project root is in the path
sys.path.append(os.getcwd())

from orchestrator.src.tools.smtp_tools import SMTPOutreachTool
from orchestrator.src.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AUTONOMOUS_VERIFY")

def verify_env_keys():
    """Checks if critical production keys are loaded."""
    load_dotenv(".env.prod")
    
    keys = [
        "STRIPE_API_KEY",
        "SMTP_USER",
        "SMTP_PASS",
        "GROQ_API_KEY"
    ]
    
    missing = []
    for key in keys:
        val = os.getenv(key)
        if not val or val == "placeholder":
            missing.append(key)
            
    if missing:
        logger.error(f"❌ MISSING REAL KEYS: {', '.join(missing)}")
        return False
    
    logger.info("✅ All critical API keys detected.")
    return True

async def test_smtp_integration():
    """Attempts to send a LIVE verification email via IONOS."""
    try:
        logger.info(f"📧 Initiating LIVE SMTP Verification (IONOS: {settings.SMTP_SERVER})...")
        
        tool = SMTPOutreachTool(None)
        
        # Override for testing - send to the user's primary email
        target = os.getenv("CONTACT_EMAIL", "robert.demotto@realms2riches.com")
        
        payload = {
            "target_email": target,
            "target_name": "Sovereign Master",
            "subject": f"System Proof of Life: {datetime.now().isoformat()}",
            "html_body": f"<h1>Sovereign Matrix Online</h1><p>Your IONOS SMTP setup is fully wired and operational.</p><p>Status: LIVE</p>"
        }
        
        result = tool.execute(payload)
        logger.info(f"SMTP Result: {result}")
        
        if result.get("status") == "success":
            logger.info("✅ SMTP Integration: VERIFIED")
            return True
        else:
            logger.error(f"❌ SMTP Integration: FAILED - {result.get('reason')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ SMTP Error: {e}")
        return False

async def test_stripe_integration():
    """Attempts to create a LIVE Stripe Checkout session."""
    try:
        import stripe
        stripe.api_key = settings.STRIPE_API_KEY
        
        logger.info("💳 Initiating LIVE Stripe Checkout test...")
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Sovereign Swarm Verification (Autonomous)',
                    },
                    'unit_amount': 2900,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://realms2riches.ai/success',
            cancel_url='https://realms2riches.ai/cancel',
        )
        
        logger.info(f"✅ Stripe Session Created: {session.url}")
        logger.info("Monetization Pipeline: VERIFIED")
        return True
    except Exception as e:
        logger.error(f"❌ Stripe Integration Error: {e}")
        return False

async def run_verification():
    print("\n  🛡️  AUTONOMOUS SOVEREIGN VERIFICATION REPORT 🛡️")
    print("  ==============================================")
    
    if not verify_env_keys():
        print("  ❌ ENV CHECK: FAILED (Missing critical keys)")
        return

    print("  ✅ ENV CHECK: PASSED")
    
    # 1. SMTP Check
    smtp_ok = await test_smtp_integration()
    
    # 2. Stripe Check
    stripe_ok = await test_stripe_integration()
    
    print("\n  ==============================================")
    if smtp_ok and stripe_ok:
        print("  🏆 SYSTEM STATUS: 100% OPERATIONAL & LIVE 🏆")
        print("  Both Outreach and Monetization are successfully wired.")
    else:
        print("  ⚠️  SYSTEM STATUS: PARTIAL SUCCESS / FAILED ⚠️")
        print(f"  SMTP: {'PASS' if smtp_ok else 'FAIL'}")
        print(f"  STRIPE: {'PASS' if stripe_ok else 'FAIL'}")
    print("  ==============================================\n")

if __name__ == "__main__":
    asyncio.run(run_verification())
