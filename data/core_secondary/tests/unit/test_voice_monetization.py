import sys
import os
sys.path.append(os.getcwd())

import pytest
from unittest.mock import MagicMock
from orchestrator.src.core.voice.session import VoiceSession, VoiceSessionState
from orchestrator.src.core.voice.mock_adapters import MockSTTAdapter, MockTTSAdapter
from orchestrator.src.core.orchestrator import Orchestrator

@pytest.fixture
def mock_voice_session():
    stt_mock = MockSTTAdapter()
    tts_mock = MockTTSAdapter()
    orch_mock = MagicMock(spec=Orchestrator)
    # Mock any orchestrator methods that might be called
    
    session = VoiceSession("test_session_id", stt_mock, tts_mock, orch_mock)
    session.context = [] # Ensure clean context for tests
    return session

@pytest.mark.asyncio
async def test_voice_session_price_inquiry(mock_voice_session):
    """Test that the voice session responds correctly to a price inquiry."""
    session = mock_voice_session
    session.stt.transcribe_chunk.return_value = "What is the price of your products?"

    await session._process_turn(b"mock_audio_data")

    assert session.state == VoiceSessionState.IDLE # Should return to idle after speaking
    assert "Our entry node, Jarvis Basic, is just $29 per month." in session.context[-1]["content"]
    assert session.output_queue.qsize() > 0 # Should have sent state, transcript, text, audio

@pytest.mark.asyncio
async def test_voice_session_cheapest_option(mock_voice_session):
    """Test that the voice session responds correctly to a 'cheapest option' inquiry."""
    session = mock_voice_session
    session.stt.transcribe_chunk.return_value = "What is the cheapest option I can get?"

    await session._process_turn(b"mock_audio_data")

    assert session.state == VoiceSessionState.IDLE
    assert "The most accessible entry point is Jarvis Basic at $29 per month." in session.context[-1]["content"]

@pytest.mark.asyncio
async def test_voice_session_send_link_request(mock_voice_session):
    """Test that the voice session responds to a 'send link' request."""
    session = mock_voice_session
    session.stt.transcribe_chunk.return_value = "Can you send me a purchase link to my email?"

    await session._process_turn(b"mock_audio_data")

    assert session.state == VoiceSessionState.IDLE
    assert "I am dispatching the secure acquisition link to your registered email now." in session.context[-1]["content"]
    assert session.context[-2]["content"] == "Can you send me a purchase link to my email?"
    # Future: patch the SMTP tool execution here to verify it was called

@pytest.mark.asyncio
async def test_voice_session_general_query(mock_voice_session):
    """Test that the voice session responds to a general inquiry."""
    session = mock_voice_session
    session.stt.transcribe_chunk.return_value = "Tell me about your services."

    await session._process_turn(b"mock_audio_data")

    assert session.state == VoiceSessionState.IDLE
    assert "I heard you say: Tell me about your services. How can I assist with your revenue fabrication today?" in session.context[-1]["content"]
