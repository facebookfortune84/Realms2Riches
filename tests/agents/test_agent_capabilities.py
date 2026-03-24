import sys
import os
sys.path.append(os.getcwd())

import pytest
import os
import json
import yaml
from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.core.config import settings

@pytest.fixture
def orchestrator():
    return Orchestrator()

@pytest.mark.anyio
async def test_architect_task_decomposition(orchestrator):
    """Verify that the Architect Agent can break down a complex goal into sub-tasks."""
    await orchestrator.startup()
    task_desc = "Design and launch a new SaaS offer for automated LinkedIn outreach using Grok."
    results = []
    async for step in orchestrator.submit_task_stream(task_desc, "test_project_001"):
        results.append(step)
    
    # Assertions
    # We expect the Architect (CYBERNETIC_ENGINEERING/Strategic_Operations) to route it
    assert any(res["status"] == "routing" for res in results)
    # Check if a 'completed' status was reached
    assert any(res["status"] == "completed" for res in results)

@pytest.mark.anyio
async def test_code_engineer_implementation(orchestrator):
    """Verify that the Code Engineer Agent can implement a simple component."""
    await orchestrator.startup()
    task_desc = "Implement a Python utility function to calculate Stripe subscription LTV."
    results = []
    async for step in orchestrator.submit_task_stream(task_desc, "test_project_002"):
        results.append(step)
    
    assert any(res["status"] == "completed" for res in results)

@pytest.mark.anyio
async def test_marketing_agent_script_generation(orchestrator):
    """Verify that the Marketing Agent can generate a viral TikTok script."""
    await orchestrator.startup()
    task_desc = "Generate a viral TikTok script for the Realms2Riches 'Sovereign Swarm' product."
    results = []
    async for step in orchestrator.submit_task_stream(task_desc, "test_project_003"):
        results.append(step)
    
    assert any(res["status"] == "completed" for res in results)

def test_agent_config_integrity():
    """Verify that all agent blueprints are valid YAML and follow the schema."""
    configs_dir = "agents/configs"
    for config_file in os.listdir(configs_dir):
        if config_file.endswith(".yaml"):
            with open(os.path.join(configs_dir, config_file), 'r') as f:
                config = yaml.safe_load(f)
                assert "agent_id" in config
                assert "role" in config
                assert "meta_dept" in config
                assert "allowed_tools" in config

def test_skill_tree_presence():
    """Ensure the Skill Tree document exists and is populated."""
    assert os.path.exists("docs/agents/skill_trees.md")
    content = open("docs/agents/skill_trees.md", 'r').read()
    assert "Engineering Skill Tree" in content
    assert "Revenue & Growth Skill Tree" in content
