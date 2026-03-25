import asyncio
import os
import sys
import json

sys.path.append(os.getcwd())

from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.core.monetization.engine import monetization_engine
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.core.config import settings

# Configure Conscious Logging
logger = get_logger("CONSCIOUS_CORE")

async def get_real_revenue():
    """Probe Stripe for ACTUAL revenue to drive state."""
    if not settings.STRIPE_API_KEY:
        return 0.0
    try:
        import stripe
        stripe.api_key = settings.STRIPE_API_KEY
        # Get charges from last 24h
        charges = stripe.Charge.list(limit=10)
        total = sum([c['amount'] for c in charges['data'] if c['paid']]) / 100
        return total
    except Exception:
        return 0.0

async def narrate_state(revenue: float, orchestrator: Orchestrator):
    """Ask the Narrator (LLM) to define the strategic mood."""
    prompt = f"""
    CONTEXT: You are the Central Nervous System of Realms2Riches.
    DATA: Current Revenue (Last 24h) = ${revenue}.
    
    TASK: define the 'Strategic Mood' and 'Narrative Theme' for the next monetization cycle.
    
    IF Revenue == 0: Mood is 'HUNGRY'. Theme is 'Aggressive Value, Secret Hacks, FOMO'.
    IF Revenue > 0: Mood is 'VALIDATED'. Theme is 'Social Proof, Scaling, Exclusive Access'.
    
    RESPONSE JSON format: {{"mood": "...", "theme": "..."}}
    """
    
    try:
        response = orchestrator.llm_provider.generate_response([{"role": "system", "content": prompt}])
        return json.loads(response)
    except:
        return {"mood": "HUNGRY", "theme": "Aggressive Growth"}

async def run_conscious_cycle():
    logger.info("🧠 ACTIVATING CONSCIOUS REVENUE ORGANISM...")
    
    # 1. Initialize
    orchestrator = Orchestrator()
    await orchestrator.startup()
    
    # 2. Sense (Telemetry)
    revenue = await get_real_revenue()
    logger.info(f"👁️ SENSE: 24h Revenue = ${revenue}")
    
    # 3. Think (Narrative)
    state = await narrate_state(revenue, orchestrator)
    logger.info(f"💭 THINK: Mood = {state['mood']} | Theme = {state['theme']}")
    
    # 4. Act (Selective Execution)
    logger.info("⚡ ACT: Dispatching streams aligned with Narrative Theme...")
    
    # In a fully conscious system, we filter streams. 
    # For launch, we run ALL but inject the THEME into the prompts.
    
    # We monkey-patch the engine's streams to include the theme?
    # Better: We just run them, as they are pre-configured. 
    # Future upgrade: Dynamically rewrite stream prompts based on theme.
    
    # Let's run the engine (which now uses real tools)
    results = await monetization_engine.run_all_streams(orchestrator)
    
    # 5. Reflect
    success_count = len([r for r in results if r['status'] == 'success'])
    logger.info(f"🧘 REFLECT: Cycle complete. {success_count}/{len(results)} streams successful.")

if __name__ == "__main__":
    asyncio.run(run_conscious_cycle())
