import random
from typing import Dict, Any, List
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.validation.schemas import ToolInvocation
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class TikTokContentGenerator(BaseTool):
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        product_name = invocation.input_data.get("product_name", "Jarvis 3.5")
        return {"status": "success", "script": f"Viral script for {product_name}"}

class EmailCampaignManager(BaseTool):
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        return {"status": "success"}

class AdCopyGenerator(BaseTool):
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        return {"status": "success"}

def get_marketing_tools() -> List[BaseTool]:
    base_schema = {"type": "object", "properties": {"product_name": {"type": "string"}}}
    return [
        TikTokContentGenerator(ToolConfig(tool_id="tiktok_gen", name="TikTok", description="Viral", parameters_schema=base_schema, allowed_agents=["*"])),
        EmailCampaignManager(ToolConfig(tool_id="email_gen", name="Email", description="B2B", parameters_schema=base_schema, allowed_agents=["*"])),
        AdCopyGenerator(ToolConfig(tool_id="ad_gen", name="Ad", description="Ads", parameters_schema=base_schema, allowed_agents=["*"]))
    ]
