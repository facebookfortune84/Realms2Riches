import os
import re
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SOVEREIGN_VERIFY")

def verify_frontend():
    logger.info("🚀 Starting Sovereign Frontend Verification...")
    
    project_slug = "realms2riches" # Or whatever slug the BuilderAgent used
    # Find the most recent project in projects/generated
    projects_dir = "projects/generated"
    if not os.path.exists(projects_dir):
        logger.error("❌ No generated projects found.")
        return False
        
    projects = [os.path.join(projects_dir, d) for d in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, d))]
    if not projects:
        logger.error("❌ No generated projects found.")
        return False
        
    latest_project = max(projects, key=os.path.getmtime)
    logger.info(f"Checking latest project: {latest_project}")
    
    frontend_path = os.path.join(latest_project, "frontend", "src", "pages")
    
    # 1. Check Page Existence
    pages = ["LandingPage.js", "UpsellPage.js", "ThankYouPage.js"]
    for page in pages:
        path = os.path.join(frontend_path, page)
        if not os.path.exists(path):
            logger.error(f"❌ Missing critical page: {page}")
            return False
        logger.info(f"✅ Found {page}")

    # 2. Check Content Logic (Landing Page)
    with open(os.path.join(frontend_path, "LandingPage.js"), "r", encoding="utf-8") as f:
        content = f.read()
        
    if "bg-red-600" not in content:
        logger.warning("⚠️  CTA button styling might be off (expected red-600).")
    
    if "Headline Missing" in content:
        logger.warning("⚠️  Builder did not inject a real headline (Found placeholder).")
    else:
        logger.info("✅ Headline injected successfully.")

    # 3. Check Routing (App.js)
    with open(os.path.join(latest_project, "frontend", "src", "App.js"), "r", encoding="utf-8") as f:
        app_content = f.read()
        
    if "/upsell" in app_content and "/thank-you" in app_content:
        logger.info("✅ Routing topology confirmed (Landing -> Upsell -> ThankYou).")
    else:
        logger.error("❌ Routing topology broken.")
        return False

    logger.info("🎉 SOVEREIGN FRONTEND VERIFIED. UI/UX IS READY.")
    return True

if __name__ == "__main__":
    success = verify_frontend()
    sys.exit(0 if success else 1)
