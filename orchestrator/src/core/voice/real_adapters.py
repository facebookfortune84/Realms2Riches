import os
import aiohttp
import io
from typing import AsyncGenerator
from orchestrator.src.core.voice.interfaces import STTAdapter, TTSAdapter
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class OpenAIWhisperAdapter(STTAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://api.openai.com/v1/audio/transcriptions"

    async def transcribe_stream(self, audio_chunk_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        """Consumes an audio stream and yields transcripts."""
        # Simple implementation: accumulate and transcribe (not real-time partials)
        buffer = b""
        async for chunk in audio_chunk_stream:
            buffer += chunk
            if len(buffer) > 32000: # ~1 second of audio
                text = await self.transcribe_chunk(buffer)
                if text: yield text
                buffer = b""
        if buffer:
            text = await self.transcribe_chunk(buffer)
            if text: yield text

    async def transcribe_chunk(self, audio_chunk: bytes) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        with aiohttp.MultipartWriter('form-data') as mp:
            part = mp.append(audio_chunk)
            part.set_content_disposition('form-data', name='file', filename='audio.wav')
            part.headers['Content-Type'] = 'audio/wav'
            mp.append("whisper-1", {'name': 'model'})

            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, data=mp, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("text", "")
                    return ""

class ElevenLabsAdapter(TTSAdapter):
    def __init__(self, api_key: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        self.api_key = api_key
        self.voice_id = voice_id
        self.base_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    async def synthesize_stream(self, text_iterator: AsyncGenerator[str, None]) -> AsyncGenerator[bytes, None]:
        url = f"{self.base_url}/stream"
        headers = {"xi-api-key": self.api_key, "Content-Type": "application/json"}
        
        async with aiohttp.ClientSession() as session:
            async for text_chunk in text_iterator:
                if not text_chunk.strip(): continue
                payload = {
                    "text": text_chunk,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
                }
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        async for chunk in resp.content.iter_chunked(1024):
                            yield chunk

    async def synthesize_text(self, text: str) -> bytes:
        url = self.base_url
        headers = {"xi-api-key": self.api_key, "Content-Type": "application/json"}
        payload = {"text": text, "model_id": "eleven_monolingual_v1"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.read()
                return b""
