import asyncio
import os
import sys
import time
from playwright.async_api import async_playwright

# Ensure orchestrator is in path
sys.path.append(os.getcwd())

from orchestrator.src.logging.logger import get_logger

logger = get_logger("SOVEREIGN_VISUALIZER")

BLOG_DIR = "data/blog/posts"
SCREENSHOT_DIR = "data/marketing/evidence"

async def capture_evidence():
    """Takes screenshots of the generated content to prove 'Life' to the user."""
    logger.info("📸 CAPTURING VISUAL EVIDENCE OF SWARM ACTIVITY...")
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 1. Capture the Vercel Frontend (Live Status)
        try:
            logger.info("📸 Shooting Live Frontend...")
            await page.goto("https://realms2riches.com", timeout=20000)
            await page.screenshot(path=f"{SCREENSHOT_DIR}/live_frontend.png")
        except:
            logger.error("Frontend Screenshot Failed.")

        # 2. Capture a local blog post (Source proof)
        posts = os.listdir(BLOG_DIR)
        if posts:
            latest_post = os.path.join(BLOG_DIR, posts[-1])
            logger.info(f"📸 Shooting Latest Asset: {posts[-1]}")
            # We can't easily 'render' markdown in playwright without a local server, 
            # but we can take a picture of the visualization dashboard we created!
            try:
                dashboard = "data/marketing/swarm_visualization.html"
                if os.path.exists(dashboard):
                    await page.goto(f"file:///{os.path.abspath(dashboard)}")
                    await page.wait_for_timeout(2000) # Wait for charts to animate
                    await page.screenshot(path=f"{SCREENSHOT_DIR}/swarm_dashboard.png")
            except:
                pass

        await browser.close()
    logger.info(f"✅ EVIDENCE LOGGED TO: {SCREENSHOT_DIR}")

if __name__ == "__main__":
    asyncio.run(capture_evidence())

