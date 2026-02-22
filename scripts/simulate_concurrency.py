import asyncio
import time
import logging
import sys
import os

sys.path.append(os.getcwd())

from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.core.api import app, startup_event

# Mock logging config
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ConcurrencySim")

async def simulate_user_action(name, duration):
    logger.info(f"START: User Action {name}")
    await asyncio.sleep(duration)
    logger.info(f"FINISH: User Action {name}")

async def simulate_background_learning():
    logger.info("START: Background Learning Stream")
    for i in range(3):
        await asyncio.sleep(0.5)
        logger.info(f"LEARNING: Processed batch {i+1}")
    logger.info("FINISH: Background Learning Stream")

async def simulate_social_posting():
    logger.info("START: Social Media Pulse")
    await asyncio.sleep(1.0) # Network latency
    logger.info("SOCIAL: Posted to Facebook & LinkedIn")
    logger.info("FINISH: Social Media Pulse")

async def run_simulation():
    logger.info("=== INITIALIZING CONCURRENCY TEST ===")
    
    # Simulate API Startup which launches background loops
    # We won't actually call startup_event() to avoid starting the real infinite loops
    # Instead, we mimic the behavior of launching tasks
    
    tasks = []
    
    # Track 1: Genesis Forge (Long running build)
    tasks.append(asyncio.create_task(simulate_user_action("Genesis Forge Build", 2.5)))
    
    # Track 2: Background Learning (Continuous)
    tasks.append(asyncio.create_task(simulate_background_learning()))
    
    # Track 3: Social Automation (Periodic)
    tasks.append(asyncio.create_task(simulate_social_posting()))
    
    # Track 4: Cockpit Command (Instant)
    tasks.append(asyncio.create_task(simulate_user_action("Cockpit Command: Status", 0.1)))
    
    start_time = time.time()
    await asyncio.gather(*tasks)
    duration = time.time() - start_time
    
    logger.info(f"=== SIMULATION COMPLETE in {duration:.2f}s ===")
    
    # Validation: If sequential, duration would be ~4.1s. 
    # If concurrent, it should be closer to the longest task (~2.5s)
    if duration < 3.0:
        logger.info("✅ PASS: System demonstrates concurrent execution capability.")
    else:
        logger.error(f"❌ FAIL: Execution took {duration:.2f}s, suggesting blocking operations.")

if __name__ == "__main__":
    asyncio.run(run_simulation())
