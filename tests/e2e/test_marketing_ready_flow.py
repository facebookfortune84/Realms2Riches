import pytest
from unittest.mock import MagicMock, patch
from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.core.llm_provider import BaseLLMProvider
from orchestrator.src.core.config import settings

class MockMarketingProvider(BaseLLMProvider):
    def generate_response(self, messages, **kwargs):
        # Simulate a marketing agent using the brand name from context
        # In a real run, the system prompt and context would contain the config
        return '{"steps": [{"tool_id": "file_tool", "inputs": {"operation": "write", "path": "test_marketing.txt", "content": "Welcome to My Brand!"}}]}'

def test_marketing_integration_flow():
    # Arrange
    # Force a known brand name in settings for the test
    settings.BRAND_NAME = "TestBrand"
    
    with patch("orchestrator.src.core.orchestrator.GroqProvider", return_value=MockMarketingProvider()):
        orchestrator = Orchestrator()
    
    # Act
    # We patch FileTool to avoid actual disk writes, but let's see if it flows
    with patch("orchestrator.src.tools.file_tools.FileTool.execute") as mock_file_exec:
        mock_file_exec.return_value = {"status": "written", "path": "test_marketing.txt"}
        
        # This task should route to the marketing/pm agent and use the mock provider
        result = orchestrator.submit_task("Generate a marketing welcome message", "proj-mkt-001")
        
    # Assert
    assert result["status"] == "completed"
    # Check if the tool was called (which means the LLM chose it and the agent ran it)
    assert mock_file_exec.called
    
    # Verify the run was recorded in the DB (SQLStore)
    runs = orchestrator.sql_store.get_runs("proj-mkt-001")
    assert len(runs) > 0
    assert runs[0].agent_id == "pm" # or whichever agent handled it
