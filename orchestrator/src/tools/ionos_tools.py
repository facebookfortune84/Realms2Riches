import base64
import requests
from typing import Dict, Any, List
from orchestrator.src.tools.base import BaseTool
from orchestrator.src.core.config import settings
from orchestrator.src.validation.schemas import ToolConfig, ToolInvocation
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class IONOSCloudTool(BaseTool):
    """
    Sovereign integration for IONOS Cloud API.
    Enables agents to manage high-availability infrastructure autonomously.
    """
    
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.base_url = "https://api.ionos.com/cloudapi/v6"

    def _get_auth_header(self) -> Dict[str, str]:
        if not settings.IONOS_PUBLIC_PREFIX or not settings.IONOS_SECRET:
            raise ValueError("IONOS credentials missing in settings.")
        
        auth_str = f"{settings.IONOS_PUBLIC_PREFIX}:{settings.IONOS_SECRET}"
        encoded_auth = base64.b64encode(auth_str.encode("ascii")).decode("ascii")
        return {"Authorization": f"Basic {encoded_auth}"}

    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        params = invocation.params or {}
        action = params.get("action")
        
        if action == "list_datacenters":
            return self.list_datacenters()
        elif action == "get_datacenter":
            return self.get_datacenter(params.get("datacenter_id"))
        elif action == "list_servers":
            return self.list_servers(params.get("datacenter_id"))
        else:
            return {
                "status": "error",
                "message": f"Unknown IONOS action: {action}"
            }

    def list_datacenters(self) -> Dict[str, Any]:
        url = f"{self.base_url}/datacenters"
        response = requests.get(url, headers=self._get_auth_header())
        response.raise_for_status()
        return response.json()

    def get_datacenter(self, datacenter_id: str) -> Dict[str, Any]:
        if not datacenter_id:
            return {"status": "error", "message": "datacenter_id required"}
        url = f"{self.base_url}/datacenters/{datacenter_id}"
        response = requests.get(url, headers=self._get_auth_header())
        response.raise_for_status()
        return response.json()

    def list_servers(self, datacenter_id: str) -> Dict[str, Any]:
        if not datacenter_id:
            return {"status": "error", "message": "datacenter_id required"}
        url = f"{self.base_url}/datacenters/{datacenter_id}/servers"
        response = requests.get(url, headers=self._get_auth_header())
        response.raise_for_status()
        return response.json()

def get_ionos_tool() -> BaseTool:
    config = ToolConfig(
        tool_id="ionos_cloud_manager",
        name="IONOS Cloud Manager",
        description="Autonomous management of IONOS Cloud infrastructure (datacenters, servers, storage).",
        parameters_schema={
            "action": "string",
            "datacenter_id": "string (optional)",
            "server_id": "string (optional)"
        },
        allowed_agents=["devops_engineer", "architect_planner"]
    )
    return IONOSCloudTool(config)
