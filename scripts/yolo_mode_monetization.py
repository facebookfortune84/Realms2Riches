import asyncio
import sys
import os

sys.path.append(os.getcwd())

from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.core.monetization.engine import monetization_engine
from orchestrator.src.logging.logger import get_logger

logger = get_logger("YOLO_MODE")

async def activate_yolo_mode():
    logger.info("🚀 ACTIVATING YOLO MODE: 100% Monetization Focus 🚀")
    
    # 1. Boot up the Orchestrator
    orchestrator = Orchestrator()
    await orchestrator.startup()
    
    logger.info("Orchestrator Swarm Online. Initiating ALL income streams...")
    
    # 2. Run all Monetization Streams
    results = await monetization_engine.run_all_streams(orchestrator)
    
    logger.info("\n💰 YOLO MODE EXECUTION RESULTS 💰")
    for res in results:
        stream_name = res.get("stream", "Unknown")
        status = res.get("status", "Unknown")
        if status == "success" or status == "executed" or status == "active":
            logger.info(f"✅ [SUCCESS] {stream_name}: {status.upper()}")
            if "links" in res:
                for link in res["links"]:
                    logger.info(f"    -> Broadcasting Link: {link}")
            if "result" in res:
                logger.info(f"    -> Agent Action: {str(res['result'])[:200]}...")
        else:
            logger.info(f"❌ [FAILED] {stream_name}: {res.get('reason', 'Unknown Error')}")
            
    logger.info("\n🏆 YOLO MODE COMPLETE. Streams are actively generating traffic and closing leads. 🏆")

if __name__ == "__main__":
    asyncio.run(activate_yolo_mode())
