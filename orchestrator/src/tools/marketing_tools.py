import json
from typing import Dict, Any, List
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.validation.schemas import ToolInvocation
from orchestrator.src.core.llm_provider import llm_provider
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class TikTokContentGenerator(BaseTool):
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        product_name = invocation.input_data.get("product_name", "Jarvis 3.5")
        
        prompt = (
            f"Generate a viral, 30-second TikTok script for {product_name}. "
            "Focus on high engagement, hook the audience in the first 3 seconds, "
            "and include a clear Call To Action (CTA). Return ONLY the script."
        )
        
        try:
            script_content = llm_provider.generate_text(prompt)
            return {"status": "success", "script": script_content, "product": product_name}
        except Exception as e:
            logger.error(f"TikTok Gen Failed: {e}")
            return {"status": "error", "reason": str(e)}

class EmailCampaignManager(BaseTool):
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        product = invocation.input_data.get("product_name", "Jarvis 3.5")
        target = invocation.input_data.get("target_audience", "B2B SaaS Founders")
        
        prompt = (
            f"Write a high-converting cold email for {product} targeting {target}. "
            "Use the AIDA framework (Attention, Interest, Desire, Action). "
            "Keep it under 200 words. Subject line included."
        )
        
        try:
            email_body = llm_provider.generate_text(prompt)
            return {"status": "success", "email_content": email_body, "target": target}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

class AdCopyGenerator(BaseTool):
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        product = invocation.input_data.get("product_name", "Jarvis 3.5")
        platform = invocation.input_data.get("platform", "Facebook")
        
        prompt = (
            f"Write 3 variations of ad copy for {product} to be run on {platform}. "
            "Focus on pain points and immediate solutions. Include emojis."
        )
        
        try:
            ad_copy = llm_provider.generate_text(prompt)
            return {"status": "success", "ad_variations": ad_copy}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

def get_marketing_tools() -> List[BaseTool]:
    base_schema = {
        "type": "object", 
        "properties": {
            "product_name": {"type": "string"},
            "target_audience": {"type": "string"},
            "platform": {"type": "string"}
        }
    }
    return [
        TikTokContentGenerator(ToolConfig(tool_id="tiktok_gen", name="TikTok Generator", description="Generates viral scripts", parameters_schema=base_schema, allowed_agents=["*"])),
        EmailCampaignManager(ToolConfig(tool_id="email_gen", name="Email Generator", description="Generates cold emails", parameters_schema=base_schema, allowed_agents=["*"])),
        AdCopyGenerator(ToolConfig(tool_id="ad_gen", name="Ad Generator", description="Generates ad copy", parameters_schema=base_schema, allowed_agents=["*"]))
    ]
