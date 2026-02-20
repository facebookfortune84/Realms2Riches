import asyncio
import uuid
from typing import Dict, Any, Optional
from enum import Enum, auto
from orchestrator.src.core.voice.interfaces import STTAdapter, TTSAdapter
from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class VoiceSessionState(Enum):
    IDLE = auto()
    LISTENING = auto()
    THINKING = auto()
    SPEAKING = auto()

class VoiceSession:
    def __init__(self, session_id: str, stt: STTAdapter, tts: TTSAdapter, orchestrator: Orchestrator):
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
                        # Simple energy/length check for interruption
                        if len(chunk) > 100: 
                            logger.info("Barge-in detected! Interrupting...")
                            await self._handle_interruption()
                            continue # Skip processing this chunk as part of old turn, or treat as new?
                                     # Usually treat as start of new turn.

                    # 2. Accumulate
                    audio_buffer.extend(chunk)
                    self.state = VoiceSessionState.LISTENING
                    
                    # 3. VAD / End-of-Speech Trigger (Mock: > 1000)
                    if len(audio_buffer) > 1000:
                        logger.info("Utterance detected, processing...")
                        
                        # Create a task for the heavy lifting so we don't block input reading
                        # But wait, if we spawn a task, we must track it to cancel it on barge-in.
                        if self.processing_task and not self.processing_task.done():
                             self.processing_task.cancel()
                        
                        # Copy buffer and clear
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
        
        # 1. Cancel the current thinking/speaking task
        if self.processing_task and not self.processing_task.done():
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
            self.processing_task = None
        
        # 2. Drain the output queue (Stop the TTS stream from sending more chunks)
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        # 3. Send explicit STOP command to frontend
        await self.output_queue.put({"type": "control", "action": "stop_audio", "reason": reason})
        
        # 4. Reset State
        self.state = VoiceSessionState.IDLE
        
        # 5. (Future) Update LLM Context with "User interrupted me"
        # self.context.append({"role": "system", "content": "User interrupted previous response."})

    async def _process_turn(self, audio_data: bytes):
        try:
            self.state = VoiceSessionState.THINKING
            await self.output_queue.put({"type": "state", "state": "thinking"})
            
            # STT
            transcript = await self.stt.transcribe_chunk(audio_data)
            await self.output_queue.put({"type": "transcript", "text": transcript, "is_final": True})
            
            # LLM
            # Mocking the Orchestrator call
            response_text = f"I heard {len(audio_data)} bytes. You said: {transcript}"
            await self.output_queue.put({"type": "text", "text": response_text})
            
            # TTS
            self.state = VoiceSessionState.SPEAKING
            await self.output_queue.put({"type": "state", "state": "speaking"})
            
            # Synthesize Stream
            async def text_gen():
                yield response_text
            
            async for audio_chunk in self.tts.synthesize_stream(text_gen()):
                await self.output_queue.put({"type": "audio", "data": audio_chunk.hex()})
                # Check for cancellation implicitly via the loop, but since we are in a task,
                # if the task is cancelled, this loop aborts automatically.

            self.state = VoiceSessionState.IDLE
            await self.output_queue.put({"type": "state", "state": "idle"})
            
        except asyncio.CancelledError:
            logger.info("Turn processing cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in turn processing: {e}")
            await self.output_queue.put({"type": "error", "message": str(e)})
