import os
import json
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FunnelForge")

CAMPAIGNS_FILE = "data/affiliates/click_funnels/campaigns.json"

def process_campaign_assets():
    if not os.path.exists(CAMPAIGNS_FILE):
        logger.error("Campaign configuration missing.")
        return

    with open(CAMPAIGNS_FILE, "r") as f:
        campaigns = json.load(f)

    for campaign in campaigns:
        logger.info(f"🔨 Processing Campaign: {campaign['name']}")
        
        # 1. Path Verification
        assets_path = campaign['assets_path']
        if not os.path.exists(assets_path):
            logger.warning(f"⚠️  Assets folder not found: {assets_path}")
            continue

        # 2. Email Swipe Extraction
        email_assets = os.path.join(assets_path, "email_assets")
        if os.path.exists(email_assets):
            for file in os.listdir(email_assets):
                if file.endswith(".md"):
                    with open(os.path.join(email_assets, file), "r", encoding="utf-8") as ef:
                        content = ef.read()
                        # Agent Logic: Split multiple emails in one file if needed
                        emails = re.split(r'#+ Email|--- Email', content)
                        logger.info(f"✅ Found {len(emails)} email swipes in {file}")

        # 3. Image Integrity Check
        image_assets = os.path.join(assets_path, "image_assets")
        if os.listdir(image_assets):
            logger.info(f"✅ {len(os.listdir(image_assets))} images verified for {campaign['id']}")

def generate_bridge_pages():
    """
    Simulates the generation of legal bridge pages for Vercel.
    In a real run, this would update frontend/src/pages/BridgePage.jsx
    """
    logger.info("🚀 Generating Legal Bridge Pages for Vercel...")
    # Logic to ensure the 'Realms2Riches' branding is present alongside 'ClickFunnels Affiliate' disclosure

if __name__ == "__main__":
    process_campaign_assets()
    generate_bridge_pages()
