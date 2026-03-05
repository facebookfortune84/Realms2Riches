import asyncio
import os
import sys

sys.path.append(os.getcwd())

from orchestrator.src.core.llm_provider import GroqProvider
from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger("GROQ_TEST")

async def test_groq():
    logger.info("🧪 TESTING GROQ CONNECTIVITY 🧪")
    
    provider = GroqProvider()
    if provider.is_mock:
        logger.error("❌ GroqProvider initialized as MOCK. Check GROQ_API_KEY in .env files.")
        return
        
    messages = [
        {"role": "system", "content": "You are a specialized revenue intelligence unit. Respond ONLY with a valid JSON object containing a 'status' field set to 'success' and a 'message' field explaining why the Realms2Riches project is ready for a multi-million dollar launch."},
        {"role": "user", "content": "Generate a final launch readiness assessment for the Sovereign Swarm."}
    ]
    
    logger.info("Step 1: Dispatching live API call to Groq...")
    try:
        response = provider.generate_response(messages)
        logger.info(f"✅ LIVE RESPONSE RECEIVED: {response}")
    except Exception as e:
        logger.error(f"❌ LIVE CALL FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_groq())
