import asyncio
import os
import sys
import pytest
from unittest.mock import MagicMock

sys.path.append(os.getcwd())

from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.validation.schemas import TaskSpec

@pytest.mark.anyio
async def test_sop_loading_and_retrieval():
    """Verify that SOPs are indexed into memory and retrieved by agents."""
    orchestrator = Orchestrator()
    await orchestrator.startup()
    
    # 1. Verify SOPs were indexed
    # Search for a specific SOP we generated
    results = orchestrator.memory.search("SOP for Cold Outreach", limit=1)
    assert len(results) > 0
    assert "SOP:" in results[0]['text']
    print(f"✅ Verified SOP Indexing: {results[0]['text'][:50]}...")

    # 2. Verify Agent Retrieves SOP during task processing
    # We'll use a real agent but a mock LLM to avoid API costs during unit tests
    test_task = TaskSpec(id="test_sop", project_id="test", description="Execute a cold outreach sequence")
    
    # Get an agent from the GLOBAL_MARKET_FORCE cell
    agent = orchestrator.cells["GLOBAL_MARKET_FORCE"].agent_pool[0]
    
    # Mock formulate_plan to see what system prompt was passed
    original_formulate = agent._formulate_plan
    agent._formulate_plan = MagicMock(return_value={"reasoning": "test", "steps": []})
    
    agent.process_task(test_task)
    
    # Check the call arguments of the mock
    args, kwargs = agent._formulate_plan.call_args
    system_prompt_passed = args[2]
    
    assert "### ACTIVE OPERATING PROCEDURE:" in system_prompt_passed
    assert "SOP: MON 012 COLD OUTREACH" in system_prompt_passed
    print("✅ Verified Agent SOP Retrieval and Injection.")

    # Restore
    agent._formulate_plan = original_formulate
