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
        Uses the Global Market Force agents to generate high-impact, authority-driven 
        social copy that weaves technical value with high-ticket CTAs.
        """
        logger.info("Social Scheduler: Waking up for Agentic Content Generation...")
        
        from orchestrator.src.core.catalog.api import catalog_api
        from orchestrator.src.core.orchestrator import Orchestrator
        
        orchestrator = Orchestrator()
        products = catalog_api.get_products()
        posts = get_all_posts()
        
        if not products or not posts:
            logger.warning("Social Scheduler: Insufficient data for broadcast.")
            return

        target_post = posts[0]
        # Always prioritize Platinum for high-impact posts
        platinum = [p for p in products if "platinum" in p.id.lower()][0]
        platinum_data = platinum.model_dump() if hasattr(platinum, "model_dump") else platinum
        
        # --- AGENTIC COPYWRITING PROMPT ---
        prompt = f"""
        You are the Chief Growth Architect of the Sovereign Intelligence Network.
        Your task is to write a VIRAL, high-authority social media post based on our latest Intelligence Report.
        
        REPORT TITLE: {target_post['title']}
        REPORT SUMMARY: {target_post['summary']}
        
        TARGET PRODUCT: {platinum_data['name']} (${platinum_data['price']})
        PRODUCT DESC: {platinum_data['description']}
        
        STYLE GUIDELINES:
        1. NO generic marketing fluff. Use high-intensity, technical, 'Sovereign' vocabulary.
        2. STRUCTURE: Hook (The Problem), Value (The Insight from the report), CTA (The Sovereign Solution).
        3. FORMAT: Short, punchy paragraphs with clear technical authority.
        4. LINK: You must end with this link: {platinum_data.get('checkout_url')}
        
        Write the copy for a LinkedIn/Facebook broadcast that will impress high-net-worth developers and founders.
        """
        
        try:
            # Generate the high-tier copy
            messages = [{"role": "system", "content": "You are a world-class Direct Response Copywriter for AI Deep Tech."}, 
                        {"role": "user", "content": prompt}]
            
            message = orchestrator.llm_provider.generate_response(messages)
            
            # Final Sanity Check: Ensure the link is present
            if platinum_data.get('checkout_url') not in message:
                message += f"\n\nSecure your position: {platinum_data.get('checkout_url')}"

            # --- VISUAL ASSET SELECTION ---
            media_url = None
            try:
                import glob
                import os
                # Using ngrok URL for external access
                base_url = "https://glowfly-sizeable-lazaro.ngrok-free.dev"
                
                # Prioritize images for this cycle
                image_files = glob.glob("data/marketing/images/*.*")
                if image_files:
                    choice = random.choice(image_files)
                    media_url = f"{base_url}/marketing/images/{os.path.basename(choice)}"
            except Exception as me:
                logger.warning(f"Social Scheduler: Asset selection failed: {me}")

            logger.info(f"Social Scheduler: Agentic copy generated. Media: {media_url}. Broadcasting...")
            
            result = self.multiplexer.execute({
                "message": message,
                "link": f"{settings.FRONTEND_URL}/blog/{target_post['slug']}",
                "media_url": media_url
            })
            
            logger.info(f"Social Scheduler: Broadcast Result - {result}")
            
        except Exception as e:
            logger.error(f"Social Scheduler: Failed to generate agentic copy. Error: {e}")
        
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
