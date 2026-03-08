import asyncio
import aiohttp
import sys
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FRONTEND_VERIFIER")

BASE_URL = "https://frontend-two-xi-gal9lkptfi.vercel.app"

# Pages to verify (Assumed based on standard SaaS structure)
# We will crawl the root to find actual links if possible, but starting with standard paths is good.
PATHS_TO_CHECK = [
    "/",
    "/pricing",
    "/blog",
    "/about",
    "/contact",
    "/features",
    "/login",
    "/dashboard"
]

async def verify_page(session, path):
    url = f"{BASE_URL}{path}"
    try:
        async with session.get(url, timeout=10) as response:
            status = response.status
            if status == 200:
                logger.info(f"✅ [200 OK] {path}")
                return True
            elif status == 404:
                logger.warning(f"❌ [404 NOT FOUND] {path}")
                return False
            else:
                logger.warning(f"⚠️ [{status}] {path}")
                return False
    except Exception as e:
        logger.error(f"❌ [ERROR] {path}: {e}")
        return False

async def main():
    logger.info(f"🔍 STARTING HEALTH CHECK FOR: {BASE_URL}")
    
    async with aiohttp.ClientSession() as session:
        # 1. Check Root
        root_ok = await verify_page(session, "/")
        if not root_ok:
            logger.critical("🚨 ROOT DOMAIN IS DOWN OR UNREACHABLE!")
            return

        # 2. Check other paths
        results = await asyncio.gather(*[verify_page(session, p) for p in PATHS_TO_CHECK if p != "/"])
        
        success_count = sum(1 for r in results if r) + (1 if root_ok else 0)
        total_count = len(PATHS_TO_CHECK)
        
        logger.info(f"\n📊 HEALTH REPORT: {success_count}/{total_count} pages active.")
        
        if success_count < total_count:
            logger.info("💡 NOTE: Some 404s are expected if the routes don't exist yet. Focus on Critical Paths (Pricing, Blog).")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
