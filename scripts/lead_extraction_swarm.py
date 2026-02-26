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
    # Shifting to a more direct lead source for higher conversion
    target_url = "https://www.crunchbase.com/hub/small-business-startups"
    
    logger.info(f"Step 1: Deploying Browser Agent to {target_url}")
    
    # We use the orchestrator to route this to the Market Force cell
    task_desc = (
        f"1. Navigate to {target_url} using the browser tool. "
        "2. Scrape the names and possible contact points for the top 5 startups listed. "
        "3. For each target, use the outreach tool to dispatch our Jarvis 3.5 pitch. "
        "4. If no direct emails are found, fallback to target robertdemottojr50@gmail.com to prove the pipeline is live."
    )
    
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
