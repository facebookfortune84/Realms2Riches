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
            f"Generate a VIRAL, AGGRESSIVE TikTok script for {product_name}. "
            "Use Neuro-Linguistic Programming (NLP) techniques. "
            "trigger: Fear of Missing Out (FOMO). "
            "Hook: 'Stop scrolling if you want to retire this year.' "
            "Call To Action: 'Link in bio or stay poor.' "
            "Format: Visual cues and dialogue."
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
            f"Write a HIGH-STAKES cold email for {product} targeting {target}. "
            "Use the 'Challenger Sale' methodology. "
            "Subject Line: Must be clickbait-worthy but professional. "
            "Body: Challenge their current broken process. Position {product} as the ONLY survival mechanism. "
            "Closing: 'I have 2 spots left.' (Scarcity). "
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
        target = invocation.input_data.get("target_audience", "General")
        
        prompt = (
            f"Write 3 variations of DIRECT RESPONSE ad copy for {product} on {platform}. "
            f"Targeting: {target}. "
            "Psychological Triggers: Greed, Status, Speed. "
            "Structure: Pattern Interrupt -> Agitate Pain -> Solved by Product. "
            "Use Emojis conservatively but effectively."
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
