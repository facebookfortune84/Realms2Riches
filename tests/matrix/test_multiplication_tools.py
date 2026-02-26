import pytest
import os
from orchestrator.src.tools.multiplication_tools import OutreachSwarmTool, SEOContentFactoryTool
from orchestrator.src.validation.schemas import ToolConfig, ToolInvocation
from orchestrator.src.core.config import settings

def test_outreach_tool_simulation():
    """Verify outreach tool works in simulation mode."""
    # Ensure SMTP is not set for this test
    settings.SMTP_USER = None
    
    tool = OutreachSwarmTool(ToolConfig(tool_id="outreach", name="Outreach", description="test", parameters_schema={}, allowed_agents=["*"]))
    
    invocation = ToolInvocation(
        tool_id="outreach",
        agent_id="test_agent",
        input_data={"target_email": "test@example.com", "target_name": "Test User"}
    )
    
    result = tool.execute(invocation)
    assert result["status"] == "success"
    assert result["action"] == "outreach_simulated"
    assert "test@example.com" in result["target"]
    assert "https://buy.stripe.com" in result["conversion_link"]

def test_seo_factory_tool():
    """Verify SEO factory generates markdown files."""
    tool = SEOContentFactoryTool(ToolConfig(tool_id="seo", name="SEO", description="test", parameters_schema={}, allowed_agents=["*"]))
    
    invocation = ToolInvocation(
        tool_id="seo",
        agent_id="test_agent",
        input_data={"topic": "AI Swarms", "keywords": ["AI", "Sovereign"]}
    )
    
    result = tool.execute(invocation)
    assert result["status"] == "success"
    assert "data/blog/technical-breakdown-ai-swarms.md" in result["blog_path"]
    
    assert os.path.exists(result["blog_path"])
    with open(result["blog_path"], "r") as f:
        content = f.read()
        assert "# AI Swarms" in content
        assert "Sovereign" in content
        assert "https://buy.stripe.com" in content
    
    # Cleanup
    if os.path.exists(result["blog_path"]):
        os.remove(result["blog_path"])
