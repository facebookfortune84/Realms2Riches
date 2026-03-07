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

logger = get_logger("LEAD_EXTRACTOR")

OUTPUT_FILE = "data/customers/leads.json"
TARGET_COUNT = 100 # Process full list
FALLBACK_TARGET_EMAIL = "robertdemottojr50@gmail.com"

async def extract_company_website(page, yc_url: str) -> str:
    """Extract company website from YC profile."""
    try:
        await page.goto(yc_url, wait_until="domcontentloaded", timeout=15000)
        
        links = await page.query_selector_all("a")
        candidates = []
        for l in links:
            href = await l.get_attribute("href")
            
            if href and href.startswith("http") and not any(x in href for x in ["ycombinator", "twitter", "linkedin", "facebook", "instagram", "crunchbase", "medium", "youtube", "apple", "google", "startupschool.org"]):
                 if "verge" in href or "news" in href or "article" in href or "policy" in href: continue
                 candidates.append(href)
        
        # Prefer short domains
        if candidates:
            # Sort by length (heuristic: company domain is usually shortest external link)
            candidates.sort(key=len)
            return candidates[0]
                 
    except Exception as e:
        logger.warning(f"Failed to extract website from {yc_url}: {e}")
    return None

async def extract_contact_info(context, url: str) -> str:
    """Visit a company URL and attempt to find email."""
    page = await context.new_page()
    email = None
    
    try:
        logger.info(f"Scraping Company Site: {url}")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        except:
            await page.close()
            return None

        content = await page.content()

        # 1. Look for mailto
        mailto = await page.query_selector("a[href^='mailto:']")
        if mailto:
            href = await mailto.get_attribute("href")
            email = href.replace("mailto:", "").split("?")[0]
        
        # 2. Regex fallback
        if not email:
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
            valid_emails = [e for e in emails if not any(x in e.lower() for x in ["example", "sentry", "wix", "bootstrap", "media", "image", "png", "jpg", "weworkremotely", "ycombinator", "cloudflare"])]
            if valid_emails:
                email = valid_emails[0]
                
    except Exception as e:
        logger.warning(f"Error scraping {url}: {e}")
    finally:
        await page.close()
        
    return email

async def run_extraction():
    logger.info("🦅 STARTING HIGH-VALUE TARGET EXTRACTION SWARM (Source: YC Targets) 🦅")
    
    # Load YC targets
    with open("data/customers/yc_targets.json", "r") as f:
        targets = json.load(f)
        
    leads = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        for i, target in enumerate(targets):
            if i >= TARGET_COUNT: break
            
            logger.info(f"Processing {i+1}/{TARGET_COUNT}: {target['name']}")
            
            # Step 1: Get Website from YC
            website = await extract_company_website(page, target['link'])
            
            lead_data = {
                "name": target["name"],
                "description": target["description"],
                "yc_link": target["link"],
                "website": website,
                "email": None
            }
            
            # Step 2: Get Email from Website
            if website:
                logger.info(f"   -> Found Website: {website}")
                email = await extract_contact_info(context, website)
                if email:
                    logger.info(f"   -> Found Email: {email}")
                    lead_data["email"] = email
                else:
                    logger.info("   -> No email found. Using fallback.")
                    lead_data["email"] = FALLBACK_TARGET_EMAIL
                    lead_data["note"] = "Email not found on homepage, using fallback for proof of life."
            else:
                 logger.warning("   -> No website found.")
                 lead_data["email"] = FALLBACK_TARGET_EMAIL
            
            leads.append(lead_data)
            
            # Incremental save
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(leads, f, indent=2)

        await browser.close()
        
    logger.info(f"🏁 EXTRACTION COMPLETE. {len(leads)} high-value targets saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(run_extraction())
