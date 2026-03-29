import uuid
import asyncio
from typing import Dict, Optional
from orchestrator.src.core.voice.interfaces import STTAdapter, TTSAdapter
from orchestrator.src.core.voice.session import VoiceSession
from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class VoiceRouter:
    def __init__(self, orchestrator: Orchestrator, stt: STTAdapter, tts: TTSAdapter):
        self.orchestrator = orchestrator
        self.stt = stt
        self.tts = tts
        self.sessions: Dict[str, VoiceSession] = {}

    def create_session(self) -> VoiceSession:
        session_id = str(uuid.uuid4())
        session = VoiceSession(session_id, self.stt, self.tts, self.orchestrator)
        self.sessions[session_id] = session
        logger.info(f"Created voice session: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[VoiceSession]:
        return self.sessions.get(session_id)

    async def handle_connection(self, websocket):
        await websocket.accept()
        session = self.create_session()
        
        # 1. Send initial session_start
        await websocket.send_json({
            "type": "session_start",
            "session_id": session.session_id
        })

        # 2. Setup bidirectional pump
        async def receive_loop():
            try:
                while True:
                    data = await websocket.receive_json()
                    if data.get("type") == "audio_chunk":
                        # Encode to bytes as VoiceSession expects 'audio' type with bytes
                        audio_bytes = data.get("data", "").encode()
                        await session.add_input({"type": "audio", "data": audio_bytes})
            except Exception as e:
                logger.info(f"Receive loop closed: {e}")
                await session.add_input({"type": "stop"})

        async def send_loop():
            try:
                while True:
                    msg = await session.get_output()
                    await websocket.send_json(msg)
            except Exception as e:
                logger.info(f"Send loop closed: {e}")

        await asyncio.gather(receive_loop(), send_loop())
