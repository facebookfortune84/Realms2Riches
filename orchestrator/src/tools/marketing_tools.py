import random
from typing import Dict, Any, List
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.validation.schemas import ToolInvocation
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class TikTokContentGenerator(BaseTool):
    """
    Generates high-viral potential scripts and descriptions for TikTok/Reels.
    Uses 'Hook-Value-CTA' framework.
    """
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        product_name = invocation.input_data.get("product_name", "AI Tool")
        link = invocation.input_data.get("link", "#")
        
        hooks = [
            f"Stop scrolling! This {product_name} changes everything.",
            f"I found the cheat code for {product_name}.",
            "POV: You just discovered the ultimate productivity hack."
        ]
        
        script = f"""
        [SCENE: Fast paced screen recording]
        VOICEOVER: {random.choice(hooks)}
        
        If you are tired of doing things the hard way, you need to see this.
        It automates the entire process in seconds.
        
        [SCENE: Demo of {product_name}]
        VOICEOVER: Just click, wait, and done. It's that simple.
        
        Link in bio to try it before they patch it!
        """
        
        description = f"SECRET REVEALED 🤫 #ai #tech #{product_name.replace(' ', '')} #fyp"
        
        return {
            "status": "success",
            "script": script,
            "description": description,
            "platform": "tiktok",
            "link": link
        }

class EmailCampaignManager(BaseTool):
    """
    Generates B2B sponsorship pitches and newsletter sequences.
    """
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        target = invocation.input_data.get("target_audience", "Tech Founders")
        product = invocation.input_data.get("product_name", "Sovereign Service")
        
        subject = f"Collaboration Opportunity: {product} x {target}"
        body = f"""
        Hi Team,
        
        We've curated a highly engaged audience of {target} who are actively looking for solutions like yours.
        
        Our 'Sovereign Intelligence' newsletter hits 10k+ verified decision-makers weekly.
        We'd love to feature {product} in our next deep-dive edition.
        
        Are you open to a sponsorship discussion?
        
        Best,
        The Realms2Riches Team
        """
        
        return {
            "status": "success",
            "subject": subject,
            "body": body,
            "type": "sponsorship_pitch"
        }

class AdCopyGenerator(BaseTool):
    """
    Generates high-CTR programmatic ad copy for platforms like Facebook/Google.
    """
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        product = invocation.input_data.get("product_name", "AI System")
        url = invocation.input_data.get("url", "#")
        
        headlines = [
            f"Scale {product} in 24 Hours",
            f"The {product} Secret is Out",
            "Automate Your Revenue Today"
        ]
        
        primary_text = f"Stop guessing. Start scaling. {product} delivers proven results for modern enterprises. Join 500+ founders using our sovereign tech stack."
        
        return {
            "status": "success",
            "headline": random.choice(headlines),
            "primary_text": primary_text,
            "cta": "Learn More",
            "url": url
        }

def get_marketing_tools() -> List[BaseTool]:
    base_schema = {"type": "object", "properties": {"product_name": {"type": "string"}, "link": {"type": "string"}}}
    
    return [
        TikTokContentGenerator(ToolConfig(tool_id="tiktok_gen", name="TikTok Generator", description="Viral Scripts", parameters_schema=base_schema, allowed_agents=["*"])),
        EmailCampaignManager(ToolConfig(tool_id="email_gen", name="Email Manager", description="B2B Copy", parameters_schema=base_schema, allowed_agents=["*"])),
        AdCopyGenerator(ToolConfig(tool_id="ad_gen", name="Ad Copywriter", description="PPC Ads", parameters_schema=base_schema, allowed_agents=["*"]))
    ]
