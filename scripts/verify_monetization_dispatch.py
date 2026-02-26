import asyncio
import os
import sys
import json

sys.path.append(os.getcwd())

from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.validation.schemas import TaskSpec

logger = get_logger("DISPATCH_VERIFIER")

async def verify_dispatch():
    logger.info("🛠️ INITIATING MILITARY-GRADE DISPATCH VERIFICATION 🛠️")
    
    orchestrator = Orchestrator()
    await orchestrator.startup()
    
    # Force a direct outreach task to your own email to prove the handshake
    test_email = "robertdemottojr50@gmail.com"
    task_desc = f"DIRECT_DIRECTIVE: Use the outreach tool to send a Jarvis 3.5 pitch to {test_email} immediately."
    
    logger.info(f"Step 1: Forcing dispatch to {test_email}")
    
    async for step in orchestrator.submit_task_stream(task_desc, "verification"):
        if step["status"] == "completed":
            logger.info("🏆 DISPATCH HANDSHAKE VERIFIED.")
            logger.info(f"Handshake Result: {json.dumps(step['result'], indent=2)}")
            
            # Final check of the log file
            if os.path.exists("data/logs/swarm_activity.log"):
                with open("data/logs/swarm_activity.log", "r") as f:
                    logs = f.readlines()
                    last_logs = logs[-10:]
                    logger.info("📊 LAST 10 LOG SIGNALS:")
                    for line in last_logs:
                        print(line.strip())
        elif step["status"] == "failed":
            logger.error(f"❌ DISPATCH FAILED: {step['reason']}")

if __name__ == "__main__":
    asyncio.run(verify_dispatch())
