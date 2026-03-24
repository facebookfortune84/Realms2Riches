import asyncio
import os
import json
import logging
from playwright.async_api import async_playwright
from datetime import datetime
from urllib.parse import urljoin, urlparse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LIVE_TEST_V520")

# Configuration
FRONTEND_URL = "https://realms2riches.com"
BACKEND_URL = "https://api.realms2riches.com"
EVIDENCE_DIR = "data/marketing/evidence"
PAGES_INDEX_FILE = "docs/marketing/live_pages_index_v5.2.0.md"

os.makedirs(EVIDENCE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(PAGES_INDEX_FILE), exist_ok=True)

async def capture_evidence(page, name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path_slug = urlparse(page.url).path.replace("/", "_").strip("_") or "root"
    filename = f"{name}_{path_slug}_{timestamp}.png"
    screenshot_path = os.path.join(EVIDENCE_DIR, filename)
    await page.screenshot(path=screenshot_path)
    logger.info(f"📸 Evidence captured: {screenshot_path}")
    return filename

async def crawl_and_verify():
    async with async_playwright() as p:
        logger.info(f"🚀 Starting Live Verification: {FRONTEND_URL}")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        discovered_pages = set()
        to_visit = [FRONTEND_URL]
        verified_pages = []

        try:
            # 1. Crawl Phase
            while to_visit and len(discovered_pages) < 20:
                current_url = to_visit.pop(0)
                if current_url in discovered_pages:
                    continue
                
                logger.info(f"Checking Page: {current_url}")
                await page.goto(current_url, wait_until="networkidle")
                discovered_pages.add(current_url)
                
                filename = await capture_evidence(page, "verified")
                title = await page.title()
                verified_pages.append({"url": current_url, "title": title, "screenshot": filename})

                # Find links
                links = await page.query_selector_all("a")
                for link in links:
                    href = await link.get_attribute("href")
                    if href:
                        full_url = urljoin(FRONTEND_URL, href)
                        if urlparse(full_url).netloc == urlparse(FRONTEND_URL).netloc:
                            if full_url not in discovered_pages:
                                to_visit.append(full_url)

            # 2. Agent Cockpit Test (Specific check)
            logger.info("--- Testing Agent Cockpit ---")
            # Usually /cockpit or /dashboard
            cockpit_url = urljoin(FRONTEND_URL, "/cockpit")
            await page.goto(cockpit_url, wait_until="networkidle")
            await capture_evidence(page, "cockpit_initial")
            
            # Look for "Submit" or "Execute" buttons
            buttons = await page.query_selector_all("button")
            for btn in buttons:
                txt = await btn.inner_text()
                if "Execute" in txt or "Run" in txt or "Submit" in txt:
                    logger.info(f"Found interaction button: {txt}")
                    # await btn.click() # Conservative: only click if safe
                    break

            # 3. Backend Health Check
            logger.info(f"--- Backend Health: {BACKEND_URL}/health ---")
            try:
                api_page = await context.new_page()
                resp = await api_page.goto(f"{BACKEND_URL}/health")
                if resp.status == 200:
                    health_data = await resp.json()
                    logger.info(f"Backend Status: {health_data}")
                    await capture_evidence(api_page, "backend_health")
            except Exception as e:
                logger.error(f"Backend offline: {e}")

        except Exception as e:
            logger.error(f"Error during crawl: {e}")
        finally:
            await browser.close()

        # Write discovered pages index
        with open(PAGES_INDEX_FILE, "w", encoding="utf-8") as f:
            f.write("# Discovered Live Pages Index v5.2.0\n\n")
            f.write("| URL | Title | Screenshot |\n")
            f.write("|-----|-------|------------|\n")
            for p in verified_pages:
                f.write(f"| {p['url']} | {p['title']} | {p['screenshot']} |\n")
        
        logger.info(f"✅ Crawl complete. Indexed {len(verified_pages)} pages.")

if __name__ == "__main__":
    asyncio.run(crawl_and_verify())

