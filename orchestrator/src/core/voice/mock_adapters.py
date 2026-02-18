import asyncio
from typing import AsyncGenerator
from orchestrator.src.core.voice.interfaces import STTAdapter, TTSAdapter
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class MockSTTAdapter(STTAdapter):
    async def transcribe_stream(self, audio_chunk_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        async for chunk in audio_chunk_stream:
            # Simulate processing delay
            await asyncio.sleep(0.1)
            # In a real implementation, this would buffer audio and yield text
            # For mock purposes, we just acknowledge the data size
            if len(chunk) > 0:
                yield f"[Mock STT: Received {len(chunk)} bytes]"

    async def transcribe_chunk(self, audio_chunk: bytes) -> str:
        return f"[Mock STT: Received {len(audio_chunk)} bytes]"

class MockTTSAdapter(TTSAdapter):
    async def synthesize_stream(self, text_stream: AsyncGenerator[str, None]) -> AsyncGenerator[bytes, None]:
        async for text in text_stream:
            logger.info(f"Synthesizing: {text}")
            yield b"MOCK_AUDIO_HEADER" + text.encode("utf-8")
            await asyncio.sleep(0.01) # Simulate real-time generation

    async def synthesize_text(self, text: str) -> bytes:
        return b"MOCK_AUDIO_HEADER" + text.encode("utf-8")
