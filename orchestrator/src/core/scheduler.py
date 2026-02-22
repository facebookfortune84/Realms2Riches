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
        # Schedule: Every 4 hours (adjust as needed to avoid spam/blocks)
        # Jitter: Add randomness to avoid bot detection patterns
        trigger = IntervalTrigger(hours=4, jitter=300) 
        self.scheduler.add_job(self.post_latest_content, trigger, id="social_poster", replace_existing=True)
        self.scheduler.start()
        logger.info("Social Scheduler started. Posting every 4 hours.")

    async def post_latest_content(self):
        """
        Rotates between sharing fresh reports and highlighting specific products from the modular registry.
        """
        logger.info("Social Scheduler: Waking up to post content...")
        
        from orchestrator.src.core.catalog.api import catalog_api
        
        # 1. Decision Logic: 70% chance report, 30% chance product spotlight
        if random.random() < 0.7:
            posts = get_all_posts()
            if not posts: return
            target_post = posts[0] 
            link = f"{settings.FRONTEND_URL}/blog/{target_post['slug']}"
            templates = [
                f"""🚀 New Intelligence Report: {target_post['title']}

{target_post['summary']}

Read more & verify: """,
                f"""⚡ Sovereign Update: {target_post['title']}

Access the full analysis here: """,
                f"""🦅 The Swarm has spoken. New insight on {target_post['title']}.

Secure your access: """
            ]
            message = random.choice(templates)
        else:
            # PRODUCT SPOTLIGHT
            products = catalog_api.get_products()
            if not products: return
            # Weighted choice: 50% chance for Platinum, 50% chance for others
            platinum = [p for p in products if "platinum" in p.id.lower()]
            others = [p for p in products if "platinum" not in p.id.lower()]
            
            if platinum and (random.random() < 0.5 or not others):
                target_p = platinum[0]
            else:
                target_p = random.choice(others if others else products)
            
            target_p = target_p.model_dump() if hasattr(target_p, "model_dump") else target_p
            link = target_p.get("checkout_url", f"{settings.FRONTEND_URL}/pricing")
            message = f"""💰 SOVEREIGN ASSET SPOTLIGHT: {target_p['name']}

{target_p['description']}

Acquire instantly: """

        logger.info(f"Social Scheduler: Broadcasting message to all channels.")
        
        try:
            # Execute the multiplexer
            # Note: The tool is synchronous (requests), so we might block the loop slightly.
            # In high-scale, use run_in_executor. Here it's fine for 2 calls.
            result = self.multiplexer.execute({
                "message": message,
                "link": link
            })
            
            logger.info(f"Social Scheduler: Result - {result}")
            
        except Exception as e:
            logger.error(f"Social Scheduler: Failed to post. Error: {e}")

# Singleton instance
social_scheduler = SocialScheduler()
