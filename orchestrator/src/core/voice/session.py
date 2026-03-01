import asyncio
import uuid
from typing import Dict, Any, Optional
from enum import Enum, auto
from orchestrator.src.core.voice.interfaces import STTInterface, TTSInterface
from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class VoiceSessionState(Enum):
    IDLE = auto()
    LISTENING = auto()
    THINKING = auto()
    SPEAKING = auto()

class VoiceSession:
    def __init__(self, session_id: str, stt: STTInterface, tts: TTSInterface, orchestrator: Orchestrator):
        self.session_id = session_id
        self.stt = stt
        self.tts = tts
        self.orchestrator = orchestrator
        
        self.state = VoiceSessionState.IDLE
        self.input_queue: asyncio.Queue = asyncio.Queue()
        self.output_queue: asyncio.Queue = asyncio.Queue()
        
        self.processing_task: Optional[asyncio.Task] = None
        self.active = True
        
        # Start the main loop
        self.loop_task = asyncio.create_task(self._processing_loop())

    async def add_input(self, data: Dict[str, Any]):
        """Called by the API layer to inject audio or events."""
        await self.input_queue.put(data)

    async def get_output(self) -> Dict[str, Any]:
        """Called by the API layer to get events to send to client."""
        return await self.output_queue.get()

    async def _processing_loop(self):
        logger.info(f"Session {self.session_id} loop started")
        audio_buffer = bytearray()
        
        while self.active:
            try:
                # Wait for input
                event = await self.input_queue.get()
                
                if event.get("type") == "stop":
                    self.active = False
                    break
                
                if event.get("type") == "audio":
                    chunk = event.get("data", b"")
                    
                    # 1. Barge-in Check
                    if self.state == VoiceSessionState.SPEAKING:
                        if len(chunk) > 100: 
                            logger.info("Barge-in detected! Interrupting...")
                            await self._handle_interruption()
                            continue

                    # 2. Accumulate
                    audio_buffer.extend(chunk)
                    self.state = VoiceSessionState.LISTENING
                    
                    # 3. Utterance Trigger
                    if len(audio_buffer) > 1000:
                        logger.info("Utterance detected, processing...")
                        
                        if self.processing_task and not self.processing_task.done():
                             self.processing_task.cancel()
                        
                        audio_data = bytes(audio_buffer)
                        audio_buffer.clear()
                        
                        self.processing_task = asyncio.create_task(self._process_turn(audio_data))
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")

    async def _handle_interruption(self, reason: str = "Audio Detected"):
        """Cancels current processing and clears output queue to stop playback immediately."""
        logger.warning(f"🛑 BARGE-IN TRIGGERED: {reason}")
        
        if self.processing_task and not self.processing_task.done():
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
            self.processing_task = None
        
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        await self.output_queue.put({"type": "control", "action": "stop_audio", "reason": reason})
        self.state = VoiceSessionState.IDLE

    async def _process_turn(self, audio_data: bytes):
        try:
            self.state = VoiceSessionState.THINKING
            await self.output_queue.put({"type": "state", "state": "thinking"})
            
            transcript = await self.stt.transcribe_chunk(audio_data)
            if not transcript or len(transcript.strip()) < 2:
                self.state = VoiceSessionState.IDLE
                return

            await self.output_queue.put({"type": "transcript", "text": transcript, "is_final": True})
            
            # --- INDUSTRIAL SCRUM LOGIC ---
            # Send the transcript to the orchestrator to get department head responses
            logger.info(f"Voice Scrum: Dispatching '{transcript}' to the matrix")
            
            # We target STRATEGIC_OPERATIONS for high-level discussion
            task_desc = f"VOICE_SCRUM_DIRECTIVE: {transcript}. Respond as the department head with a status update."
            
            async for step in self.orchestrator.submit_task_stream(task_desc, "voice_session"):
                if step["status"] == "completed":
                    res = step["result"]
                    agent_name = res.get("agent_name", "Head of Ops")
                    response_text = res.get("reasoning", "Standing by.")
                    
                    await self.output_queue.put({
                        "type": "text", 
                        "text": f"[{agent_name}]: {response_text}"
                    })
                    
                    self.state = VoiceSessionState.SPEAKING
                    await self.output_queue.put({"type": "state", "state": "speaking"})
                    
                    # Synthesize specific agent voice
                    # Fallback to default if XI_API_KEY missing
                    async def text_gen():
                        yield response_text
                    
                    async for audio_chunk in self.tts.synthesize_stream(text_gen()):
                        await self.output_queue.put({"type": "audio", "data": audio_chunk.hex()})

            self.state = VoiceSessionState.IDLE
            await self.output_queue.put({"type": "state", "state": "idle"})
            
        except asyncio.CancelledError:
            logger.info("Turn processing cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in turn processing: {e}")
            await self.output_queue.put({"type": "error", "message": str(e)})
