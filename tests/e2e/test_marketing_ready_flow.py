import sys
import os
sys.path.append(os.getcwd())

import pytest
from unittest.mock import MagicMock, patch
from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.core.llm_provider import BaseLLMProvider
from orchestrator.src.core.config import settings

class MockMarketingProvider(BaseLLMProvider):
    def generate_response(self, messages, **kwargs):
        # Simulate a marketing agent using the brand name from context
        # tool_id mapping in orchestrator.py uses 'file' for FileTool
        return '{"steps": [{"tool_id": "file", "inputs": {"operation": "write", "path": "test_marketing.txt", "content": "Welcome to My Brand!"}}], "reasoning": "Generating marketing message"}'

@pytest.mark.anyio
async def test_marketing_integration_flow():
    # Arrange
    # Force a known brand name in settings for the test
    settings.BRAND_NAME = "TestBrand"
    
    with patch("orchestrator.src.core.orchestrator.GroqProvider", return_value=MockMarketingProvider()):
        orchestrator = Orchestrator()
        await orchestrator.startup()
    
    # Act
    # We patch FileTool to avoid actual disk writes, but let's see if it flows
    with patch("orchestrator.src.tools.file_tools.FileTool.execute") as mock_file_exec:
        mock_file_exec.return_value = {"status": "written", "path": "test_marketing.txt"}
        
        # This task should route to the marketing/pm agent and use the mock provider
        results = []
        async for step in orchestrator.submit_task_stream("Generate a marketing welcome message", "proj-mkt-001"):
            results.append(step)
        
    # Assert
    final_result = results[-1]
    assert final_result["status"] == "completed"
    # Check if the tool was called (which means the LLM chose it and the agent ran it)
    assert mock_file_exec.called
