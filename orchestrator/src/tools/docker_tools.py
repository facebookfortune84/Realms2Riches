import subprocess
from typing import Dict, Any
from orchestrator.src.tools.base import BaseTool
from orchestrator.src.validation.schemas import ToolConfig, ToolInvocation

class DockerTool(BaseTool):
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        command = invocation.input_data.get("command")
        
        if command == "build":
            tag = invocation.input_data.get("tag")
            path = invocation.input_data.get("path", ".")
            subprocess.run(["docker", "build", "-t", tag, path], check=True)
            return {"status": "built", "tag": tag}
            
        elif command == "run":
            image = invocation.input_data.get("image")
            subprocess.run(["docker", "run", "-d", image], check=True)
            return {"status": "running", "image": image}
            
        else:
            raise ValueError(f"Unknown docker command: {command}")
