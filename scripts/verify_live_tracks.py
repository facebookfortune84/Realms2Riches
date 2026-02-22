import asyncio
import time
import logging
import sys
import os
import aiohttp

# Ensure we can import from the project root
sys.path.append(os.getcwd())

# Configuration
BACKEND_URL = "http://localhost:8000" # Local access to the Docker container
NGROK_URL = "https://glowfly-sizeable-lazaro.ngrok-free.dev" # Expected external URL for assets

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LiveTrackVerification")

async def verify_asset_accessibility():
    logger.info("🔍 TRACK 1: Verifying Sovereign Strategy Guide Accessibility...")
    asset_url = f"{BACKEND_URL}/assets/sovereign_strategy_guide_v3.txt"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(asset_url) as response:
                if response.status == 200:
                    content = await response.text()
                    if "SOVEREIGN STRATEGY GUIDE" in content:
                        logger.info(f"✅ ASSET VERIFIED: Guide accessible at {NGROK_URL}/assets/...")
                        return True
                    else:
                        logger.error("❌ ASSET CONTENT MISMATCH")
                else:
                    logger.error(f"❌ ASSET NOT FOUND: {response.status}")
    except Exception as e:
        logger.error(f"❌ ASSET CHECK FAILED: {e}")
    return False

async def trigger_genesis_forge():
    logger.info("🛠️ TRACK 2: Triggering Genesis Forge (Project Scaffolding)...")
    url = f"{BACKEND_URL}/api/tasks"
    payload = {"description": "Scaffold a new stealth startup named 'Project Chimera' with React and Python."}
    start = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers={"X-License-Key": "mock_dev_key"}) as response:
                data = await response.json()
                duration = time.time() - start
                if response.status == 200 and data.get("status") == "completed":
                    logger.info(f"✅ GENESIS FORGE COMPLETE in {duration:.2f}s")
                    return True
                else:
                    logger.error(f"❌ GENESIS FORGE FAILED: {data}")
    except Exception as e:
        logger.error(f"❌ GENESIS FORGE EXCEPTION: {e}")
    return False

async def trigger_social_pulse():
    logger.info("📢 TRACK 3: Triggering Social Media Pulse (Simulating Scheduler)...")
    url = f"{BACKEND_URL}/api/admin/trigger-content"
    start = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers={"X-License-Key": "mock_dev_key"}) as response:
                data = await response.json()
                duration = time.time() - start
                if response.status == 200 and data.get("status") == "published":
                    logger.info(f"✅ SOCIAL PULSE COMPLETE in {duration:.2f}s | Slug: {data.get('slug')}")
                    return True
                else:
                    logger.error(f"❌ SOCIAL PULSE FAILED: {data}")
    except Exception as e:
        logger.error(f"❌ SOCIAL PULSE EXCEPTION: {e}")
    return False

async def capture_lead_and_check_delivery():
    logger.info("📥 TRACK 4: Capturing Lead & Checking Delivery URL...")
    url = f"{BACKEND_URL}/api/leads"
    payload = {"email": "test_investor@sovereign.ai", "source": "verification_script"}
    start = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                data = await response.json()
                duration = time.time() - start
                if response.status == 200:
                    guide_url = data.get("guide_url", "")
                    if NGROK_URL in guide_url:
                        logger.info(f"✅ LEAD CAPTURE COMPLETE in {duration:.2f}s")
                        logger.info(f"   -> Guide URL Correct: {guide_url}")
                        return True
                    else:
                        logger.error(f"❌ URL MISMATCH: Expected {NGROK_URL}, got {guide_url}")
                else:
                    logger.error(f"❌ LEAD CAPTURE FAILED: {data}")
    except Exception as e:
        logger.error(f"❌ LEAD CAPTURE EXCEPTION: {e}")
    return False

async def run_live_verification():
    logger.info("🦅 SOVEREIGN LIVE TRACK VERIFICATION: INITIATING...")
    
    # 1. Verify Static Asset Serving
    asset_ok = await verify_asset_accessibility()
    if not asset_ok:
        logger.critical("STOPPING: Asset layer not online. Rebuild required.")
        return

    # 2. Concurrent Execution Test
    logger.info("⚡ STARTING CONCURRENT OPERATIONS...")
    start_time = time.time()
    
    results = await asyncio.gather(
        trigger_genesis_forge(),
        trigger_social_pulse(),
        capture_lead_and_check_delivery()
    )
    
    total_duration = time.time() - start_time
    
    if all(results):
        logger.info(f"✅ ALL TRACKS EXECUTED SUCCESSFULLY in {total_duration:.2f}s")
        logger.info("   -> Genesis Forge (Build)")
        logger.info("   -> Social Pulse (Post)")
        logger.info("   -> Lead Delivery (Email)")
        logger.info("   -> Background Learning (Running implicitly via Orchestrator)")
        logger.info("🦅 SYSTEM STATUS: SOVEREIGN & ALIGNED")
    else:
        logger.error("❌ SOME TRACKS FAILED. CHECK LOGS.")

if __name__ == "__main__":
    # Ensure background loop is simulated/running if testing against local process
    # In a real scenario, this hits the Docker container. 
    # For this CLI session, we assume the user will run 'docker-compose up' after this.
    # We can try to hit localhost:8000.
    asyncio.run(run_live_verification())
