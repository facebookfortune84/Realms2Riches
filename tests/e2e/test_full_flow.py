import sys
import os
sys.path.append(os.getcwd())

import pytest
from unittest.mock import MagicMock, patch
from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.core.llm_provider import BaseLLMProvider

class MockProvider(BaseLLMProvider):
    def generate_response(self, messages, **kwargs):
        # Return a valid JSON string for the agent to parse
        return '{"steps": [{"tool_id": "git", "inputs": {"command": "status"}}], "reasoning": "Checking git status"}'

@pytest.mark.anyio
async def test_full_flow():
    # Arrange
    with patch("orchestrator.src.core.orchestrator.GroqProvider", return_value=MockProvider()):
        orchestrator = Orchestrator()
        await orchestrator.startup()
    
    # Act
    # We patch subprocess to avoid actual side effects during CI
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = "On branch main\nnothing to commit, working tree clean"
        mock_run.return_value.returncode = 0
        
        results = []
        async for step in orchestrator.submit_task_stream("Check git status and report back", "test-project-001"):
            results.append(step)
        
    # Assert
    final_result = results[-1]
    assert final_result["status"] == "completed"
    assert "result" in final_result
    # The agent result from SovereignCell.execute
    agent_result = final_result["result"]
    assert agent_result["status"] == "completed"
