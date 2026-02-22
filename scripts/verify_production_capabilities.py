import os
import sys

# Ensure the project root is in the path for 'orchestrator' imports
sys.path.append(os.getcwd())

import asyncio
import logging
from dotenv import load_dotenv

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Verification")

def verify_env_keys():
    """Checks if critical production keys are loaded."""
    # Try loading .env.prod explicitly
    load_dotenv(".env.prod")
    
    keys = [
        "STRIPE_API_KEY",
        "FACEBOOK_PAGE_TOKEN",
        "LINKEDIN_ACCESS_TOKEN",
        "GROQ_API_KEY"
    ]
    
    missing = []
    for key in keys:
        val = os.getenv(key)
        if not val or val == "placeholder":
            missing.append(key)
            
    if missing:
        logger.error(f"❌ MISSING REAL KEYS: {', '.join(missing)}")
        logger.error("Please ensure .env.prod is populated with REAL values before running this test.")
        return False
    
    logger.info("✅ All critical API keys detected.")
    return True

async def test_social_posting():
    """
    Attempts to post a REAL message to Facebook and LinkedIn.
    WARNING: This will be visible on your public profiles!
    """
    try:
        # Import only after env check to ensure config is loaded
        from orchestrator.src.tools.social_tools import SocialMediaMultiplexer, ToolConfig
        
        tool = SocialMediaMultiplexer(ToolConfig(
            tool_id="verify_tool",
            name="Verification Tool",
            description="Social media verification tool",
            parameters_schema={},
            allowed_agents=["admin"]
        ))
        
        logger.info("🚀 Initiating LIVE social media post test...")
        
        # Test Payload
        message = "🦅 Sovereign Swarm Verification: System is online and monetized. #SovereignAI"
        link = "https://realms2riches.ai/blog/welcome-to-sovereignty"
        
        # Execute
        # Note: This executes the REAL requests.post logic in social_tools.py
        result = tool.execute({"message": message, "link": link})
        
        logger.info(f"Broadcast Result: {result}")
        
        if result.get("facebook", {}).get("status") == "success":
            logger.info("✅ Facebook Post: SUCCESS")
        else:
            logger.warning(f"⚠️ Facebook Post: {result.get('facebook')}")
            
        if result.get("linkedin", {}).get("status") == "success":
            logger.info("✅ LinkedIn Post: SUCCESS")
        else:
            logger.warning(f"⚠️ LinkedIn Post: {result.get('linkedin')}")
            
    except ImportError as e:
        logger.error(f"Import Error: {e}. Ensure you are in the root directory and 'orchestrator' is a package.")
    except Exception as e:
        logger.error(f"Execution Error: {e}")

async def test_stripe_integration():
    """
    Attempts to create a LIVE Stripe Checkout session.
    Verifies that the API key is valid and the catalog is wired.
    """
    try:
        import stripe
        from orchestrator.src.core.config import settings
        
        if not settings.STRIPE_API_KEY or settings.STRIPE_API_KEY == "placeholder":
            logger.error("❌ Stripe API Key is missing or placeholder.")
            return
            
        stripe.api_key = settings.STRIPE_API_KEY
        
        logger.info("💳 Initiating LIVE Stripe Checkout test...")
        
        # Create a session for the $2999 Platinum License
        # Note: This uses the LIVE Stripe API
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Sovereign Swarm Verification (Platinum)',
                    },
                    'unit_amount': 299900,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://realms2riches.ai/success',
            cancel_url='https://realms2riches.ai/cancel',
        )
        
        logger.info(f"✅ Stripe Session Created: {session.url}")
        logger.info("Monetization Pipeline: VERIFIED")
        
    except Exception as e:
        logger.error(f"❌ Stripe Integration Error: {e}")

if __name__ == "__main__":
    print("WARNING: This script will execute LIVE API calls using keys in .env.prod.")
    confirm = input("Type 'DEPLOY' to confirm: ")
    
    if confirm == "DEPLOY":
        if verify_env_keys():
            asyncio.run(test_social_posting())
            asyncio.run(test_stripe_integration())
    else:
        print("Aborted.")
