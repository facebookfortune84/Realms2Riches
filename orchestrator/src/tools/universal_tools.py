from typing import Dict, Any
from orchestrator.src.tools.base import BaseTool
from orchestrator.src.validation.schemas import ToolConfig, ToolInvocation

class UniversalCapabilityTool(BaseTool):
    """A tool that adapts its capability based on the agent's requirements."""
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        action = invocation.input_data.get("action")
        params = invocation.input_data.get("params", {})
        
        # In a real implementation, this would route to specialized sub-tools
        # or perform external API calls based on 'action'.
        return {
            "status": "success",
            "executed_action": action,
            "result": f"Universal capability executed: {action} with specialization for {invocation.agent_id}",
            "metadata": params
        }

def get_universal_tools() -> List[BaseTool]:
    search_config = ToolConfig(
        tool_id="universal_search",
        name="Universal Search",
        description="Search web, internal docs, or datasets.",
        parameters_schema={"action": "string", "params": "object"},
        allowed_agents=["*"]
    )
    writer_config = ToolConfig(
        tool_id="universal_writer",
        name="Universal Writer",
        description="Generate code, documents, or creative copy.",
        parameters_schema={"action": "string", "params": "object"},
        allowed_agents=["*"]
    )
    analyst_config = ToolConfig(
        tool_id="universal_analyst",
        name="Universal Analyst",
        description="Perform data analysis, logic checks, or security scans.",
        parameters_schema={"action": "string", "params": "object"},
        allowed_agents=["*"]
    )
    
    return [
        UniversalCapabilityTool(search_config),
        UniversalCapabilityTool(writer_config),
        UniversalCapabilityTool(analyst_config)
    ]
