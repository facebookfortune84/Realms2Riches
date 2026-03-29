# Runbook: Voice Mode

This guide explains how to enable, configure, and use the barge-in voice capabilities.

## Prerequisites
- Python 3.11+
- `fastapi`, `uvicorn`, `websockets` (installed via `poetry install`)
- A modern browser (for the client).

## Configuration
1.  **Edit `.env`**:
    ```bash
    VOICE_ENABLED=true
    STT_PROVIDER=mock
    TTS_PROVIDER=mock
    ```
    (Currently, only `mock` providers are implemented. To use real services, implement `STTAdapter` and `TTSAdapter` interfaces.)

## Starting the Server
The voice interface runs over WebSocket on the main FastAPI app.

1.  **Run the API Server**:
    ```bash
    uvicorn orchestrator.src.core.api:app --reload --port 8000
    ```

## Using the Client
1.  **Open the Template**:
    Open `projects/templates/voice_client/index.html` in your browser.
    
    *Note: For real microphone access, you may need to serve this file via HTTP (e.g., `python -m http.server`) due to browser security restrictions, but the mock client uses simulated button presses so local file access works fine.*

2.  **Start Session**:
    Click **"Start Session"**. You should see "Connected to server".

3.  **Simulate Speech**:
    Click **"Simulate Speech"**. This sends a mock audio payload ("Hello world") to the server.
    - You should see "Transcript: ..."
    - Then "System: ..."
    - Then "[Audio Chunk Received...]" events.

4.  **Test Barge-In**:
    Click **"Simulate Speech"** again.
    While the system is responding (streaming audio chunks), click **"Barge In"**.
    - The audio stream should stop immediately.
    - The system should acknowledge the interruption or process the new input.

## Troubleshooting
- **Connection Refused**: Ensure `uvicorn` is running on port 8000.
- **No Audio**: Check browser console logs.
- **Test Failures**: Ensure `GROQ_API_KEY` is set (even to a dummy value) for integration tests.
