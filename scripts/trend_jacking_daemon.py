import asyncio
import os
import sys
import json
from datetime import datetime
from typing import Dict

# Ensure imports
sys.path.append(os.getcwd())

from orchestrator.src.core.llm_provider import llm_provider
from orchestrator.src.logging.logger import get_logger

logger = get_logger("TREND_JACKING")

BLOG_DIR = "data/blog"
POSTS_INDEX = "data/blog/posts.json"
SLEEP_INTERVAL = 86400  # 24 hours

class TrendJackingDaemon:
    async def fetch_trends(self) -> str:
        """Simulates trend discovery. In production, this would use a Search Tool."""
        # For now, we use a high-fidelity prompt to brainstorm 'current' news angles
        prompt = "Identify a trending topic in AI Agents or Autonomous Revenue for March 2026. Write a catchy blog post title."
        return llm_provider.generate_text(prompt)

    async def generate_article(self, topic: str) -> Dict:
        """Generates a full SEO-optimized article."""
        prompt = f"""
        Write a high-stakes, industrial-grade blog post about: {topic}.
        Include:
        - Catchy Title
        - Summary
        - Body (Markdown format)
        - 3 Tags
        
        Format output as JSON with keys: title, summary, body, tags.
        """
        response = llm_provider.generate_text(prompt)
        try:
            # Basic JSON extraction if LLM wraps in markdown
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            return json.loads(response)
        except:
            return {
                "title": topic,
                "summary": "The evolution of autonomous systems.",
                "body": response,
                "tags": ["AI", "Automation"]
            }

    async def run(self):
        logger.info("🚀 TREND-JACKING DAEMON STARTED")
        while True:
            try:
                topic = await self.fetch_trends()
                logger.info(f"🔥 Trending Topic identified: {topic}")
                
                article = await self.generate_article(topic)
                slug = article['title'].lower().replace(" ", "-").replace(":", "").replace("?", "")
                
                # Save MD file
                os.makedirs(BLOG_DIR, exist_ok=True)
                md_path = os.path.join(BLOG_DIR, f"{slug}.md")
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(article['body'])
                
                # Update index
                posts = []
                if os.path.exists(POSTS_INDEX):
                    with open(POSTS_INDEX, "r") as f:
                        posts = json.load(f)
                
                # Check if already exists
                if not any(p['slug'] == slug for p in posts):
                    posts.insert(0, {
                        "slug": slug,
                        "title": article['title'],
                        "date": datetime.utcnow().strftime("%Y-%m-%d"),
                        "summary": article['summary'],
                        "tags": article['tags']
                    })
                    with open(POSTS_INDEX, "w") as f:
                        json.dump(posts, f, indent=2)
                    logger.info(f"✅ New article published: {slug}")
                
            except Exception as e:
                logger.error(f"Trend-Jacking Error: {e}")

            await asyncio.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    daemon = TrendJackingDaemon()
    try:
        asyncio.run(daemon.run())
    except KeyboardInterrupt:
        pass
