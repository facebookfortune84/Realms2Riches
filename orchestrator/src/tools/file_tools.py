import os
from typing import Dict, Any
from orchestrator.src.tools.base import BaseTool
from orchestrator.src.validation.schemas import ToolConfig, ToolInvocation

class FileTool(BaseTool):
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        operation = invocation.input_data.get("operation")
        path = invocation.input_data.get("path")
        content = invocation.input_data.get("content")
        
        # Security: ensure path is within allowed directories
        # real implementation would enforce root jail
        
        if operation == "read":
            if not os.path.exists(path):
                 raise FileNotFoundError(f"File not found: {path}")
            with open(path, "r") as f:
                return {"content": f.read()}
                
        elif operation == "write":
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return {"status": "written", "path": path}
            
        elif operation == "list":
            return {"files": os.listdir(path)}
            
        else:
            raise ValueError(f"Unknown file operation: {operation}")
