import asyncio
import json
import os
import re
import sys
from playwright.async_api import async_playwright

# Setup logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SOVEREIGN_SCRAPE")

TARGET_FILE = "data/customers/yc_targets.json"
OUTPUT_FILE = "data/generated/leads_100.json"
CONCURRENCY_LIMIT = 5

async def extract_company_website(page, yc_url: str) -> str:
    """Extract company website from YC profile."""
    try:
        await page.goto(yc_url, wait_until="domcontentloaded", timeout=15000)
        
        # Try specific button first
        website_link = await page.query_selector("a[aria-label='Company website']")
        if website_link:
            return await website_link.get_attribute("href")
        
        # Try regex on content
        content = await page.content()
        match = re.search(r'href="(https?://[^"]+)"[^>]*aria-label="Company website"', content)
        if match:
            return match.group(1)
            
        # Fallback: find external links
        links = await page.query_selector_all("a[href^='http']")
        for link in links:
            href = await link.get_attribute("href")
            if href and not any(x in href for x in ["ycombinator.com", "twitter.com", "linkedin.com", "facebook.com", "startupschool.org", "instagram.com"]):
                return href
    except Exception as e:
        logger.warning(f"Failed YC extraction for {yc_url}: {e}")
    return None

async def extract_deep_info(context, url: str):
    """Visit a company URL and attempt to find email."""
    page = await context.new_page()
    info = {
        "email": None,
        "linkedin": None
    }
    
    try:
        # logger.info(f"Deep Scraping: {url}")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        except Exception:
            # Retry once
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            except:
                return info

        content = await page.content()
        
        # 1. Email Extraction
        # Simple regex for emails
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
        
        # Filter junk
        ignore_list = ["example", "sentry", "wix", "bootstrap", "media", "image", "png", "jpg", "weworkremotely", "ycombinator", "cloudflare", "google", "amazon", "apple", "support", "info", "contact"]
        
        valid_emails = []
        for e in emails:
            e_lower = e.lower()
            if not any(x in e_lower for x in ignore_list):
                 # check file extensions
                if not e_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                    valid_emails.append(e)

        if valid_emails:
            # Prioritize "founders" or specific names over generic if possible, but for now just take first valid
            info["email"] = valid_emails[0]
            
        # 2. LinkedIn Extraction
        linkedin_match = re.search(r'(https?://(www\.)?linkedin\.com/company/[a-zA-Z0-9-]+)', content)
        if linkedin_match:
            info["linkedin"] = linkedin_match.group(1)

    except Exception as e:
        logger.warning(f"Error scraping {url}: {e}")
    finally:
        await page.close()
        
    return info

async def process_target(semaphore, context, target):
    async with semaphore:
        company_name = target.get("name")
        yc_link = target.get("link")
        
        # logger.info(f"Processing: {company_name}")
        
        result = {
            "id": target.get("id"), # Might not exist in YC json
            "name": company_name,
            "yc_link": yc_link,
            "website": None,
            "email": "robert.demotto@realms2riches.com", # Fallback
            "linkedin": None,
            "status": "failed"
        }

        page = await context.new_page()
        website = await extract_company_website(page, yc_link)
        await page.close()
        
        if website:
            result["website"] = website
            info = await extract_deep_info(context, website)
            if info["email"]:
                result["email"] = info["email"]
                result["status"] = "success"
            else:
                result["status"] = "website_found_no_email"
            
            result["linkedin"] = info["linkedin"]
        else:
            result["status"] = "no_website"
            
        logger.info(f"Finished {company_name}: {result['email']} ({result['status']})")
        return result

async def run_extraction():
    logger.info("🌌 STARTING SOVEREIGN EXTRACTION 🌌")
    
    if not os.path.exists(TARGET_FILE):
        logger.error(f"❌ Source targets missing at {TARGET_FILE}")
        return

    with open(TARGET_FILE, "r") as f:
        targets = json.load(f)
        
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        tasks = [process_target(semaphore, context, t) for t in targets]
        results = await asyncio.gather(*tasks)
        
        await browser.close()
        
    # Ensure directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
        
    logger.info(f"🏆 EXTRACTION COMPLETE. Saved {len(results)} leads to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(run_extraction())
