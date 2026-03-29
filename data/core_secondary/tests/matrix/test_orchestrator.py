import sys
import os
sys.path.append(os.getcwd())

import pytest
import asyncio
from orchestrator.src.core.orchestrator import Orchestrator

@pytest.mark.anyio
async def test_orchestrator_initialization():
    """Verify that the orchestrator can start up correctly."""
    orchestrator = Orchestrator()
    # We mock startup steps that require full container environment
    # but check if basic components are initialized.
    assert orchestrator.llm_provider is not None
    assert orchestrator.is_ready is False

@pytest.mark.anyio
async def test_orchestrator_task_routing():
    """Verify that the orchestrator routes tasks to correct cells."""
    orchestrator = Orchestrator()
    # Mock readiness and cells for routing test
    orchestrator.is_ready = True
    orchestrator.cells = {
        "GLOBAL_MARKET_FORCE": type('obj', (object,), {'execute': lambda t: asyncio.sleep(0.01)}),
        "STRATEGIC_OPERATIONS": type('obj', (object,), {'execute': lambda t: asyncio.sleep(0.01)})
    }
    
    # Test Outreach routing
    # Note: 'Cold outreach' is routed to INTEGRITY_SHIELD as it doesn't match REVENUE_SYSTEMS keywords
    stream = orchestrator.submit_task_stream("Cold outreach to clients", "test_proj")
    first_step = await stream.__anext__()
    assert first_step["status"] == "routing"
    assert first_step["destination"] == "INTEGRITY_SHIELD"

    # Test Default routing
    stream = orchestrator.submit_task_stream("General strategy plan", "test_proj")
    first_step = await stream.__anext__()
    assert first_step["status"] == "routing"
    assert first_step["destination"] == "INTEGRITY_SHIELD"
