import os
import sys
sys.path.append(os.getcwd())

import pytest
import shutil
from typing import Dict, Any
from orchestrator.src.core.agent import Agent
from orchestrator.src.validation.schemas import AgentConfig, TaskSpec
from orchestrator.src.memory.vector_store import VectorStore
from orchestrator.src.core.llm_provider import GroqProvider
from orchestrator.src.tools.base import BaseTool
from orchestrator.src.validation.schemas import ToolConfig, ToolInvocation

class MockTool(BaseTool):
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        return {"status": "success", "echo": invocation.input_data.get("message")}

@pytest.fixture
def agent_setup():
    temp_dir = "./data/test_agent_memory"
    os.makedirs(temp_dir, exist_ok=True)
    memory = VectorStore(path=temp_dir)
    
    config = AgentConfig(
        id="test_agent_123",
        name="Test Agent",
        role="Tester",
        description="Testing agents",
        system_prompt="You are a helpful test agent.",
        allowed_tool_ids=["mock_tool"]
    )
    
    tools = [
        MockTool(ToolConfig(tool_id="mock_tool", name="Mock Tool", description="Echoes input", parameters_schema={}, allowed_agents=["*"]))
    ]
    
    provider = GroqProvider()
    provider.is_mock = True
    
    agent = Agent(config, tools, memory, provider)
    
    yield agent, temp_dir
    
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    if os.path.exists("data/lineage"):
        # We don't want to delete the whole lineage dir if other tests use it, 
        # but for isolation we should.
        pass

def test_agent_initialization(agent_setup):
    agent, _ = agent_setup
    assert agent.agent_name is not None
    assert agent.dossier.agent_id == "test_agent_123"
    assert agent.dossier.tax_id.startswith("SIN-")

def test_agent_persona_adoption(agent_setup):
    agent, _ = agent_setup
    agent.adopt_persona("BOLT_ENGINEER")
    assert "Bolt" in agent.active_persona["title"]
    assert agent.dossier.persona_type == "BOLT_ENGINEER"

def test_agent_task_processing(agent_setup):
    agent, _ = agent_setup
    task = TaskSpec(
        project_id="test_proj",
        description="echo hello"
    )
    
    # Mock formulate_plan to ensure tool execution
    agent._formulate_plan = lambda p, c, s: {
        "reasoning": "Need to echo",
        "steps": [{"tool_id": "mock_tool", "inputs": {"message": "hello"}}]
    }
    
    result = agent.process_task(task)
    assert result["status"] == "completed"
    assert result["results"][0]["output_data"]["echo"] == "hello"
    assert agent.dossier.total_work_ms > 0
    assert agent.dossier.accrued_cost > 0
