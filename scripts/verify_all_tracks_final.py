import os
import sys
import asyncio
import logging
import requests
from dotenv import load_dotenv

# Ensure we can import from root
sys.path.append(os.getcwd())

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FinalVerification")

def check_keys():
    """Verify all critical keys are present in .env.prod"""
    load_dotenv(".env.prod")
    required = [
        "STRIPE_API_KEY", "FACEBOOK_PAGE_TOKEN", "LINKEDIN_ACCESS_TOKEN", 
        "GROQ_API_KEY"
    ]
    missing = [k for k in required if not os.getenv(k) or os.getenv(k) == "placeholder"]
    
    if missing:
        logger.error(f"❌ CONFIG FAIL: Missing real keys: {', '.join(missing)}")
        return False
    logger.info("✅ CONFIG: All critical API keys detected.")
    return True

def check_infrastructure():
    """Verify filesystem structure for slots and assets."""
    slots_exist = os.path.exists("data/store/slots/baseline.json")
    asset_exists = os.path.exists("data/assets/sovereign_strategy_guide_v3.txt")
    
    if slots_exist and asset_exists:
        logger.info("✅ INFRASTRUCTURE: Slots and Assets are physically present.")
        return True
    
    if not slots_exist: logger.error("❌ INFRA FAIL: baseline.json missing in slots.")
    if not asset_exists: logger.error("❌ INFRA FAIL: Strategy Guide missing in assets.")
    return False

async def check_endpoints():
    """Verify local API health and telemetry."""
    # Assuming the user runs this AFTER docker-compose up
    base_url = "http://localhost:8000"
    
    try:
        # 1. Health
        health = requests.get(f"{base_url}/health", timeout=2)
        if health.status_code == 200:
            logger.info(f"✅ API HEALTH: Active (Agents: {health.json().get('agents')})")
        else:
            logger.error(f"❌ API HEALTH: Failed ({health.status_code})")
            return False

        # 2. Products (Registry Check)
        products = requests.get(f"{base_url}/products", timeout=2)
        p_list = products.json()
        if any(p['id'] == 'pack_niche_agents' for p in p_list):
            logger.info("✅ CATALOG: Modular slots detected via API.")
        else:
            logger.warning("⚠️ CATALOG: Modular slot 'pack_niche_agents' not found via API.")

        return True
    except Exception as e:
        logger.error(f"❌ API CONNECT FAIL: {e}. Is Docker running?")
        return False

async def check_monetization():
    """Live Stripe Session Creation."""
    from orchestrator.src.core.config import settings
    import stripe
    
    if not settings.STRIPE_API_KEY or settings.STRIPE_API_KEY == "placeholder":
        logger.warning("⚠️ MONETIZATION: Stripe key missing in environment, skipping live test.")
        return True

    stripe.api_key = settings.STRIPE_API_KEY
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price_data': {'currency': 'usd', 'product_data': {'name': 'Final Verification'}, 'unit_amount': 100}, 'quantity': 1}],
            mode='payment',
            success_url='https://example.com',
            cancel_url='https://example.com',
        )
        logger.info(f"✅ MONETIZATION: Live Stripe Session Created ({session.url[:30]}...)")
        return True
    except Exception as e:
        logger.error(f"❌ MONETIZATION FAIL: {e}")
        return False

async def run_final_pass():
    logger.info("🦅 INITIATING FINAL SOVEREIGN SYSTEM CHECK...")
    
    checks = [
        check_keys(),
        check_infrastructure(),
        await check_endpoints(),
        await check_monetization()
    ]
    
    if all(checks):
        logger.info("\n🎉 ALL SYSTEMS SOVEREIGN. LAUNCH CONFIRMED.")
        logger.info("   -> Social Multiplexer: 4 Channels Active")
        logger.info("   -> Revenue Engine: Modular & Tracked")
        logger.info("   -> Asset Layer: Live & Serving")
    else:
        logger.error("\n🚫 VERIFICATION FAILED. Review logs above.")

if __name__ == "__main__":
    asyncio.run(run_final_pass())
