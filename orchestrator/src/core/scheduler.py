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
        
            from orchestrator.src.validation.conversion_auditor import LinkBeautifier, ConversionAuditor
            
            # Beautify for the prompt
            display_link = LinkBeautifier.beautify(checkout_url)
            
            prompt = f"""
            You are the Sovereign Growth Architect. Write a high-ticket sales broadcast.
            
            REPORT: {target_post['title']}
            PRODUCT: {target_p_data['name']} (${target_p_data['price']})
            LINK: {checkout_url}
            
            MANDATORY UI REQUIREMENTS:
            1. You MUST create a 'Visual Button' using emojis (e.g. [ 💳 ACQUIRE NOW ] or 【 ⚡ INITIALIZE 】).
            2. The post must end with the link clearly visible and beautified.
            3. Tone: Technically superior, elite, authoritative.
            
            {f"🚨 REPAIR PREVIOUS ERROR: {last_feedback}" if last_feedback else ""}
            """
            
            try:
                msg = o.llm_provider.generate_response([{"role": "system", "content": "Direct Response Copywriter."}, {"role": "user", "content": prompt}])
                
                # --- CONVERSION AUDIT ---
                is_valid, reason = ConversionAuditor.audit(msg, checkout_url)
                
                if is_valid:
                    # Visual Asset
                    media_url = None
                    try:
                        import glob, os
                        images = glob.glob("data/marketing/images/*.*")
                        if images:
                            media_url = f"https://glowfly-sizeable-lazaro.ngrok-free.dev/marketing/images/{os.path.basename(random.choice(images))}"
                    except: pass

                    # Attempt Broadcast
                    res = self.multiplexer.execute({"message": msg, "link": checkout_url, "media_url": media_url})
                    
                    if res.get("status") != "error":
                        logger.info("✅ SUCCESS: Post dispatched with verified conversion path.")
                        return res
                    else:
                        last_feedback = res.get("reason")
                        attempt += 1
                else:
                    last_feedback = reason
                    logger.warning(f"⚠️ AUDIT FAIL: {reason}. Kicking back to agent...")
                    attempt += 1

social_scheduler = SocialScheduler()
