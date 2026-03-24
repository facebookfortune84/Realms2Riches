import asyncio
import logging
import sys
import os

sys.path.append(os.getcwd())

from orchestrator.src.core.voice.session import VoiceSession, VoiceSessionState
from orchestrator.src.core.voice.mock_adapters import MockSTTAdapter, MockTTSAdapter
from orchestrator.src.core.orchestrator import Orchestrator

# Setup Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("BARGE_IN_TEST")

async def test_barge_in_session():
    logger.info("🎧 TESTING VOICE SESSION BARGE-IN...")
    
    # We need to mock Orchestrator init to avoid DB connections
    class MockOrchestrator:
        pass
    
    stt = MockSTTAdapter()
    tts = MockTTSAdapter()
    orch = MockOrchestrator()
    
    session = VoiceSession("test-session", stt, tts, orch)
    
    # 1. Simulate User Speech (Trigger Turn)
    logger.info("🎤 User speaks (Triggering turn)...")
    # VoiceSession triggers VAD on > 1000 bytes accumulated
    await session.add_input({"type": "audio", "data": b"x" * 1100}) 
    
    # 2. Wait for Agent to start SPEAKING
    logger.info("... Waiting for Agent to speak ...")
    while True:
        event = await session.get_output()
        logger.info(f"OUT: {event.get('type')} {event.get('state', '')}")
        if event.get("type") == "state" and event.get("state") == "speaking":
            logger.info("🤖 Agent started SPEAKING.")
            break
        
    # 3. Interrupt!
    logger.info("🎤 User interrupts (BARGE-IN)...")
    # VoiceSession interrupts if SPEAKING and chunk > 100 bytes
    await session.add_input({"type": "audio", "data": b"y" * 200}) 
    
    # 4. Expect STOP command
    stop_received = False
    try:
        # We expect it relatively quickly
        event = await asyncio.wait_for(session.get_output(), timeout=2.0)
        logger.info(f"OUT: {event}")
        if event.get("type") == "control" and event.get("action") == "stop_audio":
            logger.info("✅ RECEIVED STOP COMMAND. Barge-in successful.")
            stop_received = True
        else:
            # Check next few events
            for _ in range(5):
                 event = await asyncio.wait_for(session.get_output(), timeout=1.0)
                 logger.info(f"OUT: {event}")
                 if event.get("type") == "control" and event.get("action") == "stop_audio":
                     logger.info("✅ RECEIVED STOP COMMAND. Barge-in successful.")
                     stop_received = True
                     break
    except asyncio.TimeoutError:
        logger.error("❌ Timeout waiting for stop command.")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        
    if not stop_received:
        logger.error("❌ Failed to receive stop command.")
    else:
        logger.info("🏆 TEST PASSED.")
        
    # Cleanup
    await session.add_input({"type": "stop"})
    
if __name__ == "__main__":
    asyncio.run(test_barge_in_session())
