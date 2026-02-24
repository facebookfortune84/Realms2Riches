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
    def __init__(self, orchestrator=None):
        self.scheduler = AsyncIOScheduler()
        self.orchestrator = orchestrator
        self.multiplexer = SocialMediaMultiplexer(ToolConfig(
            tool_id="social_scheduler_multiplexer", name="Automated Social Poster",
            description="Scheduled poster", parameters_schema={}, allowed_agents=["system"]
        ))
        
    def start(self):
        trigger = IntervalTrigger(hours=1, jitter=60) 
        self.scheduler.add_job(self.post_latest_content, trigger, id="social_poster", replace_existing=True)

        from orchestrator.src.core.monetization.engine import monetization_engine
        monetization_trigger = IntervalTrigger(minutes=30, jitter=15)
        self.scheduler.add_job(monetization_engine.run_all_streams, monetization_trigger, id="monetization_engine_run", replace_existing=True)

        self.scheduler.start()
        logger.info("Social Scheduler & Monetization Engine: HIGH VELOCITY ACTIVE")

    async def post_latest_content(self):
        logger.info("Social Scheduler: Initiating Direct-to-Stripe Dispatch Cycle...")
        if not self.orchestrator or not self.orchestrator.is_ready: return {"status": "skipped", "reason": "Initializing."}

        from orchestrator.src.core.catalog.api import catalog_api
        from orchestrator.src.validation.conversion_auditor import ConversionAuditor
        
        products = catalog_api.get_products()
        posts = get_all_posts()
        if not products or not posts: return {"status": "skipped", "reason": "No content."}

        target_post = posts[0]
        platinum = [p for p in products if "platinum" in p.id.lower()]
        target_p = platinum[0] if (platinum and random.random() < 0.8) else random.choice(products)
        
        checkout_url = 'https://buy.stripe.com/test_platinum_2999'
        if hasattr(target_p, 'checkout_url') and target_p.checkout_url != "#":
            checkout_url = target_p.checkout_url

        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Dispatch Attempt {attempt}/{max_attempts}...")
            prompt = f"Write technical social copy for {target_p.name}. URL: {checkout_url}. Include button [💳 ACQUIRE NOW]."
            
            try:
                msg = self.orchestrator.llm_provider.generate_response([{"role": "system", "content": "Chief Growth Architect."}, {"role": "user", "content": prompt}])
                is_valid, reason = ConversionAuditor.audit(msg, checkout_url)
                
                if is_valid:
                    media_url = None
                    try:
                        import glob
                        # AUDIT OPTIMIZATION: USE IMAGES ONLY FOR 100% RELIABILITY
                        images = glob.glob("data/marketing/images/*.png") + glob.glob("data/marketing/images/*.jpg")
                        if images:
                            filename = os.path.basename(random.choice(images))
                            media_url = f"https://glowfly-sizeable-lazaro.ngrok-free.dev/marketing/images/{filename}"
                    except: pass

                    res = self.multiplexer.execute({"message": msg, "link": checkout_url, "media_url": media_url})
                    # Check if at least one platform succeeded
                    if any(r.get("status") == "success" for r in res.values()):
                        logger.info(f"✅ DISPATCH SUCCESS: {res}")
                        return res
                    else:
                        logger.error(f"Dispatch Failed on all channels: {res}")
                else:
                    logger.warning(f"Conversion Audit Failed (Attempt {attempt}): {reason}")
            except Exception as e:
                logger.error(f"Scheduler Loop Error: {e}")
                break
        
        return {"status": "error", "reason": "Max attempts reached."}

social_scheduler = SocialScheduler()
