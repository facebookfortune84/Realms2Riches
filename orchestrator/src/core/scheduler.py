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
        trigger = IntervalTrigger(hours=4, jitter=300) 
        self.scheduler.add_job(self.post_latest_content, trigger, id="social_poster", replace_existing=True)
        self.scheduler.start()
        logger.info("Social Scheduler started. Cycle: 4 hours.")

    async def post_latest_content(self):
        logger.info("Social Scheduler: Initiating Agentic Dispatch Cycle...")
        from orchestrator.src.core.catalog.api import catalog_api
        from orchestrator.src.core.orchestrator import Orchestrator
        
        o = Orchestrator()
        products = catalog_api.get_products()
        posts = get_all_posts()
        if not products or not posts: return

        target_post = posts[0]
        # Weighted choice for product (favor Platinum)
        platinum = [p for p in products if "platinum" in p.id.lower()]
        target_p = platinum[0] if platinum else products[0]
        target_p_data = target_p.model_dump() if hasattr(target_p, "model_dump") else target_p
        checkout_url = target_p_data.get('checkout_url', 'https://glowfly-sizeable-lazaro.ngrok-free.dev')

        max_attempts = 3
        attempt = 1
        last_feedback = ""
        
        while attempt <= max_attempts:
            logger.info(f"Dispatch Attempt {attempt}/{max_attempts}...")
            
            prompt = f"""
            You are the Sovereign Growth Architect. Write an 'Impressive', high-authority social broadcast.
            
            TARGET INTEL: {target_post['title']} - {target_post['summary']}
            TARGET ASSET: {target_p_data['name']} (${target_p_data['price']})
            MANDATORY CTA LINK: {checkout_url}
            
            RULES:
            1. STYLE: Zero fluff. Technical, elite, sovereign tone.
            2. HOOK: Start with a technical bottleneck or architectural insight from the report.
            3. ACTION: You MUST use a strong action verb (e.g. SECURE, ACQUIRE, INITIALIZE, DEPLOY) before the link.
            4. FORMAT: Use short paragraphs and impactful technical vocabulary.
            5. GOAL: Prove technical superiority, then offer immediate acquisition.
            
            {f"🚨 REPAIR PREVIOUS ERROR: {last_feedback}" if last_feedback else ""}
            """
            
            try:
                msg = o.llm_provider.generate_response([{"role": "system", "content": "Copywriter."}, {"role": "user", "content": prompt}])
                
                # Visual Asset
                media_url = None
                try:
                    import glob
                    images = glob.glob("data/marketing/images/*.*")
                    if images:
                        media_url = f"https://glowfly-sizeable-lazaro.ngrok-free.dev/marketing/images/{os.path.basename(random.choice(images))}"
                except: pass

                # Attempt Broadcast
                res = self.multiplexer.execute({"message": msg, "link": checkout_url, "media_url": media_url})
                
                if res.get("status") != "error":
                    logger.info("✅ SUCCESS: Post dispatched.")
                    return res
                elif res.get("error_type") == "validation_fail":
                    last_feedback = res.get("reason")
                    logger.warning(f"⚠️ SELF-HEALING: Attempt {attempt} failed: {last_feedback}")
                    attempt += 1
                else:
                    logger.error(f"❌ FATAL ERROR: {res.get('reason')}")
                    break
            except Exception as e:
                logger.error(f"Loop Error: {e}")
                break

social_scheduler = SocialScheduler()
