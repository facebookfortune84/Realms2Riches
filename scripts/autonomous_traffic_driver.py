import asyncio
import random
import logging
import json
import os
import requests
import time
from datetime import datetime

# Import core components (assumes PYTHONPATH is set correctly)
from orchestrator.src.agents.content_factory import ContentFactoryAgent
from orchestrator.src.tools.media_tools import ImageGenerationTool, ToolConfig
from orchestrator.src.core.llm_provider import llm_provider

# Configure Logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [GROWTH_ENGINE] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/growth_engine.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GrowthEngine")

class GrowthEngine:
    def __init__(self):
        self.target_url = "https://realms2riches.com"
        self.api_url = "https://api.realms2riches.com"
        self.campaigns_dir = "data/marketing/campaigns"
        os.makedirs(self.campaigns_dir, exist_ok=True)
        
        # Initialize Agents
        # We pass None for orchestrator if the agent doesn't strictly need it for LLM calls
        self.content_factory = ContentFactoryAgent(orchestrator=None) 
        self.media_tool = ImageGenerationTool(ToolConfig(name="img_gen", description=""))
        
        self.is_running = True

    async def start(self):
        logger.info(f"🚀 Initializing Sovereign Growth Engine for {self.target_url}")
        
        while self.is_running:
            try:
                # 1. Generate a Fresh Campaign (if needed)
                campaign = await self.generate_daily_campaign()
                
                # 2. Execute Traffic Missions based on Campaign
                await self.execute_campaign(campaign)
                
                # Wait between waves
                sleep_time = random.randint(60, 300)
                logger.info(f"💤 Cycle complete. Cooling down for {sleep_time}s...")
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"❌ Engine failure: {e}")
                await asyncio.sleep(30)

    async def generate_daily_campaign(self):
        """Generates a full set of marketing assets for the day."""
        today = datetime.now().strftime("%Y-%m-%d")
        campaign_id = f"campaign_{today}"
        campaign_path = os.path.join(self.campaigns_dir, f"{campaign_id}.json")
        
        if os.path.exists(campaign_path):
            logger.info(f"📂 Loading existing campaign: {campaign_id}")
            with open(campaign_path, "r") as f:
                return json.load(f)
        
        logger.info(f"🎨 Generating NEW Daily Campaign: {campaign_id}")
        
        # 1. Generate Copy
        assets = self.content_factory.generate_campaign_assets(
            product_context="Realms2Riches - The World's First Sovereign Autonomous Monetization Matrix",
            angle="Escape the Platform Trap (Sovereignty)"
        )
        
        # 2. Generate Visuals
        logger.info("🖼️ Synthesizing Ad Creatives...")
        if "assets" in assets and "social_posts" in assets["assets"]:
            for post in assets["assets"]["social_posts"]:
                if "image_prompt" in post:
                    img_result = self.media_tool.rotate_assets(post["image_prompt"])
                    if img_result["status"] == "success":
                        post["image_url"] = img_result["champion"]["url"]
                        post["local_path"] = img_result["champion"]["local_path"]

        # 3. Save Campaign
        campaign_data = {
            "id": campaign_id,
            "created_at": str(datetime.now()),
            "assets": assets
        }
        
        with open(campaign_path, "w") as f:
            json.dump(campaign_data, f, indent=2)
            
        logger.info(f"✅ Campaign Generated & Saved: {campaign_path}")
        return campaign_data

    async def execute_campaign(self, campaign):
        """Simulates traffic driven by the generated assets."""
        logger.info(f"⚔️ Executing Campaign: {campaign['id']}")
        
        # Social Wave
        social_posts = campaign.get("assets", {}).get("assets", {}).get("social_posts", [])
        if social_posts:
            logger.info(f"📢 'Posting' {len(social_posts)} social pieces to the ether...")
            # Simulate clicks proportional to content quality (mocked)
            await self.simulate_traffic_wave("social_viral", 20, 60)

        # Email Blast
        emails = campaign.get("assets", {}).get("assets", {}).get("cold_email", {})
        if emails:
            logger.info(f"📨 'Sending' Cold Outreach: {emails.get('subject_lines', ['Hi'])[0]}")
            await self.simulate_traffic_wave("email_outreach", 5, 15)

    async def simulate_traffic_wave(self, source, min_clicks, max_clicks):
        count = random.randint(min_clicks, max_clicks)
        logger.info(f"🌊 Incoming Wave from {source}: {count} visitors")
        
        for _ in range(count):
            try:
                requests.get(f"{self.api_url}/r?target={self.target_url}&source={source}&campaign=autogen_v1", timeout=5)
            except:
                pass
            await asyncio.sleep(random.uniform(0.1, 0.5))

if __name__ == "__main__":
    engine = GrowthEngine()
    try:
        asyncio.run(engine.start())
    except KeyboardInterrupt:
        logger.info("🛑 Growth Engine stopped.")
