import os
import subprocess
from typing import Dict, Any
from orchestrator.src.tools.base import BaseTool
from orchestrator.src.validation.schemas import ToolConfig, ToolInvocation

class GitTool(BaseTool):
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        command = invocation.input_data.get("command")
        repo_path = invocation.input_data.get("path", ".")
        
        if command == "clone":
            url = invocation.input_data.get("url")
            subprocess.run(["git", "clone", url, repo_path], check=True)
            return {"status": "cloned", "path": repo_path}
            
        elif command == "commit":
            message = invocation.input_data.get("message")
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", message], cwd=repo_path, check=True)
            return {"status": "committed", "message": message}
            
        elif command == "status":
            result = subprocess.run(["git", "status"], cwd=repo_path, capture_output=True, text=True)
            return {"status": result.stdout}
            
        else:
            raise ValueError(f"Unknown git command: {command}")
