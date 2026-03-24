import sys
import os
sys.path.append(os.getcwd())

import pytest
from orchestrator.src.tools.browser_agent import BrowserAgentTool
from orchestrator.src.validation.schemas import ToolConfig, ToolInvocation

def test_browser_agent_registration():
    """Verify tool registration."""
    tool = BrowserAgentTool(ToolConfig(tool_id="browser", name="Browser", description="test", parameters_schema={}, allowed_agents=["*"]))
    assert tool.config.tool_id == "browser"

def test_browser_agent_initialization():
    """Verify tool initialized correctly."""
    tool = BrowserAgentTool(ToolConfig(tool_id="browser", name="Browser", description="test", parameters_schema={}, allowed_agents=["*"]))
    assert tool.browser is None
    assert tool.context is None
