import asyncio
import json
import logging
import sys
import os
from playwright.async_api import async_playwright
from datetime import datetime

# Ensure orchestrator is in path
sys.path.append(os.getcwd())

from orchestrator.src.tools.seo_tools import SEOTool, ToolConfig
from orchestrator.src.core.llm_provider import llm_provider

# Setup Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("TREND_JACKER")

class TrendJackingSwarm:
    def __init__(self):
        self.seo_tool = SEOTool(ToolConfig(tool_id="seo_factory", name="SEO", description="SEO", parameters_schema={}, allowed_agents=["*"]))
        self.trends = []

    async def scrape_hacker_news(self):
        """Scrapes the top stories from Hacker News."""
        logger.info("🕵️ [SCOUT] TARGETING: Hacker News...")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto("https://news.ycombinator.com/", timeout=15000)
                await page.wait_for_selector(".athing")
                titles = await page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('.titleline > a')).slice(0, 5).map(a => a.innerText);
                }''')
                await browser.close()
                logger.info(f"✅ [HN] ACQUIRED: {titles}")
                self.trends.extend(titles)
        except Exception as e:
            logger.error(f"❌ [HN] FAILED: {e}")

    async def scrape_reddit_tech(self):
        """Scrapes top posts from r/technology (simulated via JSON for speed/reliability if auth fails, or playwright)."""
        logger.info("🕵️ [SCOUT] TARGETING: Reddit (r/technology)...")
        # Using Playwright for Reddit can be tricky due to anti-bot, but let's try a public json feed approach which is robust
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("https://www.reddit.com/r/technology/top.json?limit=5", headers={"User-Agent": "Mozilla/5.0"}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        titles = [post['data']['title'] for post in data['data']['children']]
                        logger.info(f"✅ [REDDIT] ACQUIRED: {titles}")
                        self.trends.extend(titles)
                    else:
                        logger.warning(f"⚠️ [REDDIT] BLOCKED ({resp.status}). Using fallback.")
        except Exception as e:
            logger.error(f"❌ [REDDIT] FAILED: {e}")

    async def generate_contrarian_takes(self):
        """Generates 'Hot Takes' on the scraped topics."""
        if not self.trends:
            return

        logger.info("🧠 ACTIVATING NEURAL OPINION ENGINE...")
        
        for trend in self.trends:
            prompt = (
                f"Topic: {trend}\n"
                "Task: Write a provocative, contrarian LinkedIn post that goes against the popular narrative. "
                "Hook the reader instantly. Use short, punchy sentences. "
                "Goal: Maximum engagement/comments. "
                "End with: 'Prove me wrong. 👇'"
            )
            
            try:
                content = llm_provider.generate_text(prompt)
                logger.info(f"🔥 HOT TAKE GENERATED FOR '{trend}':\n{content[:100]}...")
                
                # We also turn this into a Blog Post
                logger.info(f"📝 CONVERTING TO LONG-FORM ASSET...")
                self.seo_tool.execute({
                    "action": "generate_and_publish",
                    "keywords": [trend, "Tech News", "Analysis"],
                    "content": content # Seed content
                })
                
            except Exception as e:
                logger.error(f"Generation Error: {e}")

    async def run(self):
        self.trends = [] # Reset
        await self.scrape_hacker_news()
        await self.scrape_reddit_tech()
        
        # Deduplicate
        self.trends = list(set(self.trends))
        logger.info(f"🧠 AGGREGATED INTELLIGENCE: {len(self.trends)} targets.")
        
        await self.generate_contrarian_takes()

if __name__ == "__main__":
    swarm = TrendJackingSwarm()
    asyncio.run(swarm.run())
