from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from orchestrator.src.core.voice.router import VoiceRouter
from orchestrator.src.core.voice.mock_adapters import MockSTTAdapter, MockTTSAdapter
from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.logging.logger import get_logger
import asyncio
import json

logger = get_logger(__name__)

app = FastAPI()

# In a real app, use dependency injection or a lifespan manager
orchestrator = Orchestrator()
stt = MockSTTAdapter()
tts = MockTTSAdapter()
voice_router = VoiceRouter(orchestrator, stt, tts)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.websocket("/ws/voice")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session = voice_router.create_session()
    
    # Send initial session info
    await websocket.send_json({"type": "session_start", "session_id": session.session_id})

    # Start a background task to push events from session -> client
    output_task = asyncio.create_task(send_output(websocket, session))
    
    try:
        while True:
            # Simple text-based JSON protocol for this demo
            data = await websocket.receive_text()
            
            try:
                msg = json.loads(data)
                msg_type = msg.get("type")
                
                if msg_type == "audio_chunk":
                    # Simulate audio arrival. In real app, this might be binary.
                    # Here we take "data" string and encode it to bytes to mimic audio
                    audio_content = msg.get("data", "").encode("utf-8")
                    await session.add_input({"type": "audio", "data": audio_content})
                elif msg_type == "stop":
                    await session.add_input({"type": "stop"})
                    break
                elif msg_type == "control":
                    # E.g. forced barge-in signal from client
                    action = msg.get("action")
                    if action == "interrupt":
                        # Manually trigger interruption logic
                        # But session logic handles barge-in on audio arrival too
                        pass

            except json.JSONDecodeError:
                logger.warning("Invalid JSON received")
                
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {session.session_id}")
    finally:
        output_task.cancel()
        if session.session_id in voice_router.sessions:
            del voice_router.sessions[session.session_id]

async def send_output(websocket: WebSocket, session):
    try:
        while True:
            event = await session.output_queue.get()
            if event:
                await websocket.send_json(event)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Error sending output: {e}")
