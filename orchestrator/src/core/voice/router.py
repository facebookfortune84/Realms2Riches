import asyncio
import logging
from typing import Optional, Dict, Any
from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.core.voice.interfaces import STTInterface, TTSInterface

logger = logging.getLogger(__name__)

class VoiceRouter:
    """
    Advanced Multimodal Router with Barge-In Support.
    Allows real-time interruption of agent synthesis.
    """
    def __init__(self, orchestrator: Orchestrator, stt: STTInterface, tts: TTSInterface):
        self.orchestrator = orchestrator
        self.stt = stt
        self.tts = tts
        self.active_session_id: Optional[str] = None
        self.interrupt_flag = asyncio.Event()

    async def handle_audio_stream(self, audio_chunk: bytes, session_id: str):
        """
        Processes incoming audio and triggers BARGE-IN if speech is detected 
        while an agent is speaking.
        """
        # 1. Trigger Barge-In Interruption
        if self.active_session_id == session_id:
            logger.info("🎙️ BARGE-IN DETECTED: Interrupting active synthesis...")
            self.interrupt_flag.set()
            
        # 2. Transcribe
        text = await self.stt.transcribe(audio_chunk)
        if not text: return

        # 3. Process with Orchestrator
        self.active_session_id = session_id
        self.interrupt_flag.clear()
        
        async for step in self.orchestrator.submit_task_stream(text, f"voice_{session_id}"):
            if step.get("status") == "completed":
                response_text = step["result"].get("reasoning", "Directive understood.")
                await self._synthesize_and_stream(response_text, session_id)

    async def _synthesize_and_stream(self, text: str, session_id: str):
        """Synthesizes response with interruption checks."""
        logger.info(f"Synthesizing: {text[:50]}...")
        
        # In a real streaming implementation, we would check the 
        # interrupt_flag between audio packets.
        if self.interrupt_flag.is_set():
            logger.warning("Synthesis aborted due to user barge-in.")
            return

        audio = await self.tts.synthesize(text)
        # Emit audio to websocket (handled in api.py)
        return audio

    def request_interruption(self):
        """Manually trigger a barge-in event."""
        self.interrupt_flag.set()
