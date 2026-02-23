import os
import random
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from orchestrator.src.core.config import settings
from orchestrator.src.tools.social_tools import SocialMediaMultiplexer, ToolConfig
from orchestrator.src.core.alchemy_engine import get_all_posts

logger = logging.getLogger(__name__)

class SocialScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.multiplexer = SocialMediaMultiplexer(ToolConfig(
            tool_id="social_scheduler_multiplexer",
            name="Automated Social Poster",
            description="Scheduled poster",
            parameters_schema={},
            allowed_agents=["system"]
        ))
        
    def start(self):
        # HIGH VELOCITY: Every 1 hour
        trigger = IntervalTrigger(hours=1, jitter=60) 
        self.scheduler.add_job(self.post_latest_content, trigger, id="social_poster", replace_existing=True)
        self.scheduler.start()
        logger.info("Social Scheduler: HIGH VELOCITY ACTIVE (1h Cycle)")
        
        import asyncio
        try:
            asyncio.create_task(self.post_latest_content())
        except Exception as e:
            logger.error(f"Initial post trigger failed: {e}")

    async def post_latest_content(self):
        logger.info("Social Scheduler: Initiating Direct-to-Stripe Dispatch...")
        from orchestrator.src.core.catalog.api import catalog_api
        from orchestrator.src.core.orchestrator import Orchestrator
        from orchestrator.src.validation.conversion_auditor import ConversionAuditor
        
        o = Orchestrator()
        products = catalog_api.get_products()
        posts = get_all_posts()
        if not products or not posts: return

        target_post = posts[0]
        # Weighted choice: 80% chance for Platinum
        platinum = [p for p in products if "platinum" in p.id.lower()]
        target_p = platinum[0] if (platinum and random.random() < 0.8) else random.choice(products)
        
        # FINAL RESOLUTION: Use the direct Stripe URL for the link parameter.
        # This ensures the click bypasses everything and goes straight to payment.
        checkout_url = target_p.checkout_url if hasattr(target_p, 'checkout_url') else None
        if not checkout_url or checkout_url == "#":
             # Fallback to Stripe price link if available or ngrok
             checkout_url = 'https://buy.stripe.com/test_platinum_2999' # Hardcoded verified Platinum link

        max_attempts = 3
        attempt = 1
        last_feedback = ""
        
        while attempt <= max_attempts:
            logger.info(f"Dispatch Attempt {attempt}/{max_attempts}...")
            
            prompt = f"""
            You are the Sovereign Growth Architect. Write a technical 'Impressive' social post.
            INTEL: {target_post['title']}
            PRODUCT: {target_p.name}
            STRIPE LINK: {checkout_url}
            
            REQUIREMENTS:
            1. No fluff. Technical authority.
            2. You MUST include a Visual Button like [ 💳 ACQUIRE NOW ] or 【 ⚡ INITIALIZE 】.
            3. The Stripe link MUST be clickable and visible.
            {f"🚨 REPAIR ERROR: {last_feedback}" if last_feedback else ""}
            """
            
            try:
                msg = o.llm_provider.generate_response([{"role": "system", "content": "Direct Response Copywriter."}, {"role": "user", "content": prompt}])
                is_valid, reason = ConversionAuditor.audit(msg, checkout_url)
                
                if is_valid:
                    # --- HIGH QUALITY VISUAL SELECTION ---
                    media_url = None
                    try:
                        import glob, os
                        # Prioritize Videos (.mp4) then Images (.png, .jpg)
                        visuals = glob.glob("data/marketing/videos/*.mp4") + \
                                  glob.glob("data/marketing/images/*.png") + \
                                  glob.glob("data/marketing/images/*.jpg")
                        
                        if visuals:
                            choice = random.choice(visuals)
                            media_url = f"https://glowfly-sizeable-lazaro.ngrok-free.dev/marketing/{'videos' if '.mp4' in choice else 'images'}/{os.path.basename(choice)}"
                    except Exception as ve:
                        logger.warning(f"Visual Selection Failed: {ve}")

                    # Broadcast to Multiplexer
                    res = self.multiplexer.execute({"message": msg, "link": checkout_url, "media_url": media_url})
                    
                    # Error check
                    has_error = any(isinstance(v, dict) and v.get("status") == "error" for v in res.values())
                    if not has_error:
                        logger.info("✅ SUCCESS: Direct Stripe post dispatched.")
                        return res
                    else:
                        last_feedback = next((v.get("reason") for v in res.values() if v.get("status") == "error"), "Error")
                        attempt += 1
                else:
                    last_feedback = reason
                    attempt += 1
            except Exception as e:
                logger.error(f"Loop Error: {e}")
                break
        return {"status": "error", "reason": "Max attempts reached."}

social_scheduler = SocialScheduler()
