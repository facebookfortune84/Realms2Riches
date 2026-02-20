import os
import aiohttp
import io
from orchestrator.src.core.voice.interfaces import STTAdapter, TTSAdapter
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class OpenAIWhisperAdapter(STTAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://api.openai.com/v1/audio/transcriptions"

    async def transcribe_chunk(self, audio_chunk: bytes) -> str:
        # In a real stream, we might buffer or use a websocket.
        # For this implementation, we send the chunk as a file.
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        # Create a multipart writer
        with aiohttp.MultipartWriter('form-data') as mp:
            part = mp.append(audio_chunk)
            part.set_content_disposition('form-data', name='file', filename='audio.wav')
            part.headers['Content-Type'] = 'audio/wav'
            
            mp.append("whisper-1", {'name': 'model'})

            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, data=mp, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        text = data.get("text", "")
                        if text:
                            logger.info(f"Whisper heard: {text}")
                        return text
                    else:
                        err = await resp.text()
                        logger.error(f"Whisper API Error: {err}")
                        return ""

class ElevenLabsAdapter(TTSAdapter):
    def __init__(self, api_key: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        self.api_key = api_key
        self.voice_id = voice_id
        self.url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"

    async def synthesize_stream(self, text_iterator):
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async for text_chunk in text_iterator:
                if not text_chunk.strip(): continue
                
                payload = {
                    "text": text_chunk,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
                }
                
                async with session.post(self.url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        # Stream the audio bytes back
                        async for chunk in resp.content.iter_chunked(1024):
                            yield chunk
                    else:
                        logger.error(f"ElevenLabs Error: {await resp.text()}")
