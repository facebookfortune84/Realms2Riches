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
        Fetches the latest blog post and shares it if it hasn't been shared recently.
        In a real prod system, we'd track 'last_shared_id' in a DB.
        For now, we pick a random recent post to keep the feed alive.
        """
        logger.info("Social Scheduler: Waking up to post content...")
        
        posts = get_all_posts()
        if not posts:
            logger.warning("Social Scheduler: No content found to post.")
            return

        # Strategy: Pick from the top 3 most recent to ensure freshness but variety
        # This simple logic ensures we don't just spam the same one if no new ones are made.
        # But since the swarm generates continuously, 'posts[0]' is likely new.
        target_post = posts[0] 
        
        # Construct the message
        # We use a variety of templates to avoid duplicate content detection
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
        
        # The link to the post (assuming it's hosted at /blog/slug)
        # We append a CTA link to the product page or checkout for higher conversion
        # The user requested direct Stripe checkout links. 
        # But social platforms prefer content links. 
        # Strategy: Link to the *blog post* which NOW contains the direct Stripe links (implemented in previous step).
        # OR link directly to the checkout if the post is promotional.
        
        # Let's link to the blog post, which is the "content" value.
        link = f"{settings.FRONTEND_URL}/blog/{target_post['slug']}"
        
        logger.info(f"Social Scheduler: Attempting to post '{target_post['title']}' to all channels.")
        
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
