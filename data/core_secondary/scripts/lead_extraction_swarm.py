import asyncio
import os
import sys
import json
import re
from playwright.async_api import async_playwright
from sqlalchemy.future import select
from arq import create_pool
from arq.connections import RedisSettings

# Ensure we can import from orchestrator
sys.path.append(os.getcwd())

from orchestrator.src.logging.logger import get_logger
from orchestrator.src.core.database import AsyncSessionLocal
from orchestrator.src.core.models import Lead, LeadStatus
from orchestrator.src.core.config import settings

logger = get_logger("HDRB_EXTRACTOR")

TARGET_FILE = "data/customers/yc_targets.json"
CONCURRENCY_LIMIT = 5 # Reduced for stability in "Sovereign" mode

async def extract_company_website(page, yc_url: str) -> str:
    """Extract company website from YC profile."""
    try:
        await page.goto(yc_url, wait_until="domcontentloaded", timeout=30000)
        website_link = await page.query_selector("a[aria-label='Company website']")
        if website_link:
            return await website_link.get_attribute("href")
        
        content = await page.content()
        match = re.search(r'href="(https?://[^"]+)"[^>]*aria-label="Company website"', content)
        if match:
            return match.group(1)
            
        links = await page.query_selector_all("a[href^='http']")
        for link in links:
            href = await link.get_attribute("href")
            if not any(x in href for x in ["ycombinator.com", "twitter.com", "linkedin.com", "facebook.com", "startupschool.org"]):
                return href
    except Exception as e:
        logger.warning(f"Failed YC extraction for {yc_url}: {e}")
    return None

async def extract_deep_info(context, url: str):
    """Visit a company URL and attempt to find email and context."""
    page = await context.new_page()
    info = {
        "email": None,
        "linkedin": None,
        "meta_data": {"scraped_text": []}
    }
    
    try:
        logger.info(f"Deep Scraping: {url}")
        await page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        
        content = await page.content()
        
        # 1. Email Extraction
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
        valid_emails = [e for e in emails if not any(x in e.lower() for x in ["example", "sentry", "wix", "bootstrap", "media", "image", "png", "jpg", "weworkremotely", "ycombinator", "cloudflare", "google", "amazon", "apple"])]
        if valid_emails:
            info["email"] = valid_emails[0] # Take first valid
            
        # 2. LinkedIn Extraction
        linkedin_match = re.search(r'(https?://(www\.)?linkedin\.com/company/[a-zA-Z0-9-]+)', content)
        if linkedin_match:
            info["linkedin"] = linkedin_match.group(1)
            
        # 3. Context/Hook Extraction (First 500 chars of visible text)
        # Simple extraction of headers or paragraphs
        elements = await page.query_selector_all("h1, h2, p")
        text_content = []
        for el in elements[:5]:
            txt = await el.inner_text()
            if txt and len(txt) > 20:
                text_content.append(txt.strip())
        info["meta_data"]["scraped_text"] = text_content

    except Exception as e:
        logger.warning(f"Error scraping {url}: {e}")
    finally:
        await page.close()
        
    return info

async def process_target(semaphore, context, target, redis_pool):
    async with semaphore:
        company_name = target.get("name")
        yc_link = target.get("link")
        
        logger.info(f"🚀 Processing: {company_name}")
        
        # 1. Check if already exists in DB
        async with AsyncSessionLocal() as session:
            stmt = select(Lead).where(Lead.company == company_name)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                logger.info(f"Skipping {company_name}, already in DB.")
                return

        # 2. Scrape
        page = await context.new_page()
        website = await extract_company_website(page, yc_link)
        await page.close()
        
        if not website:
            logger.warning(f"No website found for {company_name}")
            return

        info = await extract_deep_info(context, website)
        
        if not info["email"]:
            logger.info(f"No email found for {company_name}")
            # Still save but mark as needing manual enrichment? Or just skip.
            # For automation, skip if no email.
            return

        # 3. Save to DB
        async with AsyncSessionLocal() as session:
            new_lead = Lead(
                company=company_name,
                website=website,
                email=info["email"],
                linkedin_url=info["linkedin"],
                meta_data=info["meta_data"],
                status=LeadStatus.SCRAPED,
                source="YC_Scraper"
            )
            session.add(new_lead)
            await session.commit()
            await session.refresh(new_lead)
            lead_id = new_lead.id
            logger.info(f"✅ Saved Lead: {company_name} ({info['email']})")

        # 4. Enqueue Task
        if redis_pool:
            # We enqueue the email task directly (or an enrichment task first)
            # For now, let's enqueue an email task assuming we have a template
            # In a real scenario, we'd generate the hook first.
            # Let's enqueue 'generate_hook_and_send' (simulated by send_email_task with placeholder)
            
            # Actually, let's just log it. The Daemon should pick it up.
            pass

async def run_extraction():
    logger.info("🌌 STARTING SOVEREIGN EXTRACTION SWARM 🌌")
    
    if not os.path.exists(TARGET_FILE):
        logger.error("❌ Source targets missing.")
        return

    with open(TARGET_FILE, "r") as f:
        targets = json.load(f) #[:TARGET_COUNT]
        
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    # Connect to Redis for task enqueuing (optional here if we just use DB polling)
    redis = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL or "redis://localhost:6379"))
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 Sovereign/1.0")
        
        tasks = [process_target(semaphore, context, t, redis) for t in targets]
        await asyncio.gather(*tasks)
        
        await browser.close()
        
    await redis.close()
    logger.info("🏆 EXTRACTION COMPLETE.")

if __name__ == "__main__":
    asyncio.run(run_extraction())
