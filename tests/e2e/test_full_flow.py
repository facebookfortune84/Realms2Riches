import pytest
from unittest.mock import MagicMock, patch
from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.core.llm_provider import BaseLLMProvider

class MockProvider(BaseLLMProvider):
    def generate_response(self, messages, **kwargs):
        # Return a valid JSON string for the agent to parse
        return '{"steps": [{"tool_id": "git_tool", "inputs": {"command": "status"}}]}'

def test_full_flow():
    # Arrange
    with patch("orchestrator.src.core.orchestrator.GroqProvider", return_value=MockProvider()):
        orchestrator = Orchestrator()
    
    # Act
    # We patch subprocess to avoid actual side effects during CI
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = "On branch main\nnothing to commit, working tree clean"
        mock_run.return_value.returncode = 0
        
        result = orchestrator.submit_task("Check git status and report back", "test-project-001")
        
    # Assert
    assert result["status"] == "completed"
    assert len(result["results"]) > 0
    # Since we mocked the LLM to call git status if "git" is in prompt:
    # Check if git tool was invoked
    assert result["results"][0]["status"] == "success"
