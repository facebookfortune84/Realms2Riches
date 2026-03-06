from abc import ABC, abstractmethod
from typing import Dict, Any, List
from orchestrator.src.validation.schemas import ToolConfig, ToolInvocation
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class BaseTool(ABC):
    def __init__(self, config: ToolConfig):
        self.config = config

    @abstractmethod
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        """Execute the tool logic."""
        pass

    def validate_inputs(self, invocation: ToolInvocation) -> bool:
        # Pydantic handles basic type validation, but specific logic can go here
        return True

    def run(self, invocation: ToolInvocation) -> ToolInvocation:
        logger.info(f"Running tool {self.config.tool_id} for agent {invocation.agent_id}")
        
        # Guard against None input
        if invocation.input_data is None:
            invocation.input_data = {}

        if not self.validate_inputs(invocation):
            invocation.status = "failure"
            invocation.error_message = "Input validation failed"
            return invocation

        try:
            # Standardized: Pass the entire invocation object
            result = self.execute(invocation)
            if isinstance(result, dict):
                invocation.output_data = result
            elif hasattr(result, "model_dump"):
                invocation.output_data = result.model_dump(mode="json")
            
            invocation.status = "success"
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            invocation.status = "failure"
            invocation.error_message = str(e)
        
        return invocation
