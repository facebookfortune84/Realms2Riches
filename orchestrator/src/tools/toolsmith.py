import os
import hashlib
import importlib.util
from typing import Dict, Any
from orchestrator.src.tools.base import BaseTool
from orchestrator.src.validation.schemas import ToolConfig, ToolInvocation
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class ToolSmith(BaseTool):
    """Allows agents to programmatically create new tools for the swarm."""
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        tool_name = invocation.input_data.get("tool_name")
        code = invocation.input_data.get("code")
        
        if not tool_name or not code:
            return {"status": "error", "message": "Name and Code required"}

        # Security: Safe directory
        path = f"orchestrator/src/tools/dynamic/{tool_name}.py"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Write the new tool
        with open(path, "w") as f:
            f.write(code)
            
        # Integrity verification
        tool_hash = hashlib.sha256(code.encode()).hexdigest()
        
        logger.info(f"Forge ToolSmith: Forged new tool {tool_name} with hash {tool_hash[:8]}")
        
        return {
            "status": "forged",
            "tool_name": tool_name,
            "integrity_hash": tool_hash,
            "path": path
        }

def get_toolsmith() -> BaseTool:
    config = ToolConfig(
        tool_id="recursive_toolsmith",
        name="The Forge ToolSmith",
        description="Allows the swarm to evolve by creating and registering new Python tools.",
        parameters_schema={"tool_name": "string", "code": "string"},
        allowed_agents=["agent_cybernetic_engineering_1"]
    )
    return ToolSmith(config)
