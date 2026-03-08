import asyncio
import os
import sys
import json
import re
from playwright.async_api import async_playwright
from typing import List, Dict

# Ensure we can import from orchestrator if needed
sys.path.append(os.getcwd())

from orchestrator.src.logging.logger import get_logger

logger = get_logger("HDRB_EXTRACTOR")

OUTPUT_FILE = "data/customers/leads.json"
TARGET_COUNT = 100 
CONCURRENCY_LIMIT = 10 # Number of simultaneous browser tabs/instances

async def extract_company_website(page, yc_url: str) -> str:
    """Extract company website from YC profile."""
    try:
        await page.goto(yc_url, wait_until="domcontentloaded", timeout=20000)
        website_link = await page.query_selector("a[href^='http']:not([href*='ycombinator']):not([href*='twitter']):not([href*='linkedin'])")
        if website_link:
            return await website_link.get_attribute("href")
    except Exception as e:
        logger.warning(f"Failed YC extraction for {yc_url}: {e}")
    return None

async def extract_contact_info(context, url: str) -> str:
    """Visit a company URL and attempt to find email."""
    page = await context.new_page()
    email = "robertdemottojr83@gmail.com" # Default fallback
    
    try:
        logger.info(f"Deep Scraping: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        content = await page.content()
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
        valid_emails = [e for e in emails if not any(x in e.lower() for x in ["example", "sentry", "wix", "bootstrap", "media", "image", "png", "jpg", "weworkremotely", "ycombinator", "cloudflare"])]
        if valid_emails:
            email = valid_emails[0]
    except Exception as e:
        logger.warning(f"Error scraping {url}: {e}")
    finally:
        await page.close()
        
    return email

async def process_target(semaphore, context, target):
    async with semaphore:
        company_name = target.get("name")
        yc_link = target.get("link")
        
        logger.info(f"🚀 Processing: {company_name}")
        
        page = await context.new_page()
        website = await extract_company_website(page, yc_link)
        await page.close()
        
        email = "robertdemottojr83@gmail.com"
        if website:
            email = await extract_contact_info(context, website)
            
        return {
            "name": company_name,
            "description": target.get("description"),
            "yc_link": yc_link,
            "website": website,
            "email": email,
            "timestamp": json.dumps(str(asyncio.get_event_loop().time()))
        }

async def run_extraction():
    logger.info("🌌 STARTING HIGH-DENSITY PARALLEL EXTRACTION 🌌")
    
    if not os.path.exists("data/customers/yc_targets.json"):
        logger.error("❌ Source targets missing.")
        return

    with open("data/customers/yc_targets.json", "r") as f:
        targets = json.load(f)[:TARGET_COUNT]
        
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 Sovereign/1.0")
        
        tasks = [process_target(semaphore, context, t) for t in targets]
        leads = await asyncio.gather(*tasks)
        
        # Filter and save
        final_leads = [l for l in leads if l]
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(final_leads, f, indent=2)

        await browser.close()
        
    logger.info(f"🏆 HDRB EXTRACTION COMPLETE. {len(final_leads)} targets ready for blitz.")

if __name__ == "__main__":
    asyncio.run(run_extraction())
