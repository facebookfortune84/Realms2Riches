import uuid
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
