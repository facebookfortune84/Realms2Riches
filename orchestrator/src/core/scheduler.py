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
        
        # HIGH VELOCITY: Trigger a post immediately on startup
        import asyncio
        asyncio.create_task(self.post_latest_content())

    async def post_latest_content(self):
        logger.info("Social Scheduler: Initiating Agentic Dispatch Cycle...")
        # ... (setup code)
        
        while attempt <= max_attempts:
            # ... (prompt & generation code)
            
            try:
                # ... (media selection)

                # Attempt Broadcast
                res = self.multiplexer.execute({"message": msg, "link": checkout_url, "media_url": media_url})
                
                # CORRECTED SUCCESS CHECK: Ensure no errors in channel results
                has_error = any(isinstance(v, dict) and v.get("status") == "error" for v in res.values())
                
                if not has_error:
                    logger.info(f"✅ SUCCESS: Post dispatched to all channels on attempt {attempt}.")
                    return res
                else:
                    # Find the specific error reason for feedback
                    last_feedback = next((v.get("reason") for v in res.values() if v.get("status") == "error"), "Unknown error")
                    logger.warning(f"⚠️ SELF-HEALING: Attempt {attempt} failed: {last_feedback}")
                    attempt += 1
            except Exception as e:
                logger.error(f"Loop Error: {e}")
                break

social_scheduler = SocialScheduler()
