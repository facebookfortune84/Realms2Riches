from abc import ABC, abstractmethod
from typing import AsyncGenerator, Generator, Optional, Any

class STTAdapter(ABC):
    @abstractmethod
    async def transcribe_stream(self, audio_chunk_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        """
        Consumes an audio stream and yields partial or final text transcripts.
        """
        pass

    @abstractmethod
    async def transcribe_chunk(self, audio_chunk: bytes) -> str:
        """
        Transcribes a single chunk of audio (e.g., a complete utterance).
        """
        pass

class TTSAdapter(ABC):
    @abstractmethod
    async def synthesize_stream(self, text_stream: AsyncGenerator[str, None]) -> AsyncGenerator[bytes, None]:
        """
        Consumes a text stream and yields audio chunks.
        """
        pass
        
    @abstractmethod
    async def synthesize_text(self, text: str) -> bytes:
        """
        Synthesizes a complete text string into audio bytes.
        """
        pass
