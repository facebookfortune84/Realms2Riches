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
        # High Velocity: Every 1 hour
        trigger = IntervalTrigger(hours=1, jitter=60) 
        self.scheduler.add_job(self.post_latest_content, trigger, id="social_poster", replace_existing=True)
        self.scheduler.start()
        logger.info("Social Scheduler: HIGH VELOCITY ACTIVE (1h Cycle)")
        
        # Immediate Startup Pulse
        import asyncio
        try:
            asyncio.create_task(self.post_latest_content())
        except Exception as e:
            logger.error(f"Startup dispatch failed: {e}")

    async def post_latest_content(self):
        """Uses Global Market Force agents with a Self-Healing Loop."""
        logger.info("Social Scheduler: Initiating Direct-to-Stripe Dispatch Cycle...")
        
        from orchestrator.src.core.catalog.api import catalog_api
        from orchestrator.src.core.orchestrator import Orchestrator
        from orchestrator.src.validation.conversion_auditor import LinkBeautifier, ConversionAuditor
        
        o = Orchestrator()
        products = catalog_api.get_products()
        posts = get_all_posts()
        
        if not products or not posts:
            logger.warning("Social Scheduler: No products/posts. Skipping.")
            return {"status": "skipped", "reason": "No content."}

        target_post = posts[0]
        platinum = [p for p in products if "platinum" in p.id.lower()]
        target_p = platinum[0] if (platinum and random.random() < 0.8) else random.choice(products)
        
        # Direct Stripe Link
        checkout_url = target_p.checkout_url if hasattr(target_p, 'checkout_url') else None
        if not checkout_url or checkout_url == "#":
             checkout_url = 'https://buy.stripe.com/test_platinum_2999'

        max_attempts = 3
        attempt = 1
        last_feedback = ""
        
        while attempt <= max_attempts:
            logger.info(f"Dispatch Attempt {attempt}/{max_attempts}...")
            
            prompt = f"""
            You are the Chief Growth Architect. Write a high-authority technical social post.
            REPORT: {target_post['title']} - {target_post['summary']}
            PRODUCT: {target_p.name}
            REQUIRED LINK: {checkout_url}
            
            MANDATORY UI:
            1. You MUST include a 'Visual Button' like [ 💳 ACQUIRE NOW ].
            2. The direct link MUST be at the very top or bottom.
            3. Tone: Technically superior, no fluff.
            {f"🚨 REPAIR ERROR: {last_feedback}" if last_feedback else ""}
            """
            
            try:
                msg = o.llm_provider.generate_response([{"role": "system", "content": "Copywriter."}, {"role": "user", "content": prompt}])
                
                # Conversion Audit
                is_valid, reason = ConversionAuditor.audit(msg, checkout_url)
                
                if is_valid:
                    # Media Selection
                    media_url = None
                    try:
                        import glob
                        # Skip SVGs
                        visuals = glob.glob("data/marketing/videos/*.mp4") + \
                                  glob.glob("data/marketing/images/*.png") + \
                                  glob.glob("data/marketing/images/*.jpg")
                        if visuals:
                            choice = random.choice(visuals)
                            media_url = f"https://glowfly-sizeable-lazaro.ngrok-free.dev/marketing/{'videos' if '.mp4' in choice else 'images'}/{os.path.basename(choice)}"
                    except: pass

                    # Dispatch
                    res = self.multiplexer.execute({"message": msg, "link": checkout_url, "media_url": media_url})
                    
                    # Verify no channel errors
                    has_error = any(isinstance(v, dict) and v.get("status") == "error" for v in res.values())
                    if not has_error:
                        logger.info(f"✅ SUCCESS: Post dispatched on attempt {attempt}.")
                        return res
                    else:
                        last_feedback = next((v.get("reason") for v in res.values() if v.get("status") == "error"), "Error")
                        attempt += 1
                else:
                    last_feedback = reason
                    attempt += 1
            except Exception as e:
                logger.error(f"Scheduler Loop Error: {e}")
                break
        
        return {"status": "error", "reason": "Max attempts reached."}

social_scheduler = SocialScheduler()
