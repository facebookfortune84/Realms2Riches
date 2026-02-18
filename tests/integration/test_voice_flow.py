from fastapi.testclient import TestClient
from orchestrator.src.core.api import app
import pytest

def test_voice_session_flow():
    with TestClient(app) as client:
        with client.websocket_connect("/ws/voice") as websocket:
            # 1. Connection established
            data = websocket.receive_json()
            assert data["type"] == "session_start"
            session_id = data["session_id"]
            
            # 2. Simulate User Speech
            # Send enough data to trigger VAD (mock threshold > 1000 bytes)
            # "audio_chunk" with "data" string -> server encodes to bytes
            mock_audio_payload = "A" * 1500
            websocket.send_json({"type": "audio_chunk", "data": mock_audio_payload})
            
            # 3. Read events: expect state transitions -> transcript -> text -> state:speaking -> audio chunks
            transcript_received = False
            speaking_state_reached = False
            
            # Loop to consume events until we see speaking state
            # Max iterations to avoid infinite loop
            for _ in range(50):
                try:
                    msg = websocket.receive_json()
                    msg_type = msg.get("type")
                    
                    if msg_type == "transcript":
                        transcript_received = True
                    elif msg_type == "state" and msg.get("state") == "speaking":
                        speaking_state_reached = True
                        break
                except Exception:
                    break
            
            assert transcript_received, "Transcript was not received"
            assert speaking_state_reached, "System did not enter SPEAKING state"
            
            # 4. Barge-in Test
            # System is now streaming audio chunks (mock TTS)
            # Send interruption payload (> 100 bytes to trigger barge-in logic)
            interruption_payload = "BargeIn" * 20 # ~140 chars/bytes
            websocket.send_json({"type": "audio_chunk", "data": interruption_payload})
            
            # Expect system to stop audio (drain queue or stop sending) and return to IDLE (or processing if VAD triggered)
            # Mock VAD threshold is high, so small interruption just stops current TTS and buffers new audio
            # We expect state -> idle eventually
            
            idle_reached = False
            for _ in range(50):
                try:
                    msg = websocket.receive_json()
                    if msg.get("type") == "state" and msg.get("state") == "idle":
                        idle_reached = True
                        break
                except Exception:
                    break
            
            assert idle_reached, "System did not return to IDLE after interruption"
