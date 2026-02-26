import asyncio
import os
import sys

sys.path.append(os.getcwd())

from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.logging.logger import get_logger

logger = get_logger("LEAD_SWARM")

async def run_extraction_swarm():
    logger.info("🦅 INITIATING HIGH-DENSITY LEAD EXTRACTION 🦅")
    
    orchestrator = Orchestrator()
    await orchestrator.startup()
    
    # Target: High-value B2B directories or specific niche searches
    # For this first run, we'll target a generic B2B search to prove the pipeline
    target_url = "https://www.google.com/search?q=small+business+owners+contact+list+linkedin"
    
    logger.info(f"Step 1: Deploying Browser Agent to {target_url}")
    
    # We use the orchestrator to route this to the Market Force cell
    task_desc = f"Use the browser tool to navigate to {target_url}, scrape at least 10 high-value B2B contact emails, and then for each email found, execute the outreach tool to send our Jarvis 3.5 pitch."
    
    async for step in orchestrator.submit_task_stream(task_desc, "lead_generation"):
        if step["status"] == "routing":
            logger.info(f"   -> Routing to {step['destination']}")
        elif step["status"] == "completed":
            logger.info("✅ SWARM TASK COMPLETE.")
            logger.info(f"Result Summary: {str(step['result'])[:500]}...")
        elif step["status"] == "failed":
            logger.error(f"❌ SWARM FAILED: {step['reason']}")

if __name__ == "__main__":
    asyncio.run(run_extraction_swarm())
