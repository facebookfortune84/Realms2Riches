import random
from typing import Dict, Any, List
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.validation.schemas import ToolInvocation
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class TikTokContentGenerator(BaseTool):
    """
    Generates high-viral potential scripts and descriptions for TikTok/Reels.
    Pass 3 Upgrade: Enhanced SEO and conversion hooks.
    """
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        product_name = invocation.input_data.get("product_name", "Jarvis 3.5")
        link = invocation.input_data.get("link", "https://buy.stripe.com/5kQcN5aHLdIdbAS4dd8so02")
        
        # SEO-Optimized Hooks
        hooks = [
            f"How to automate 100% of your B2B outreach with {product_name}.",
            f"The secret tech YC founders are using to scale: {product_name}.",
            "Stop hiring VAs. Use autonomous swarms instead."
        ]
        
        script = f"""
        [SCENE: Matrix-style terminal scrolling fast]
        VOICEOVER: {random.choice(hooks)}
        
        This is not a GPT wrapper. This is a Sovereign Intelligence Unit.
        It generates its own leads, writes its own copy, and closes its own sales.
        
        [SCENE: Stripe dashboard showing $499.00 payments]
        VOICEOVER: The results are live. The engine is breathing.
        
        Click the link to secure your license before the next epoch begins.
        """
        
        # High-Density SEO Metadata
        description = f"Autonomous Revenue Engine 🚀 #ai #saas #monetization #jarvis #sovereign #wealthtech"
        
        return {
            "status": "success",
            "script": script,
            "seo_metadata": {
                "keywords": ["autonomous agents", "automated revenue", "jarvis 3.5", "ai outreach"],
                "cta_power_score": 0.98
            },
            "description": description,
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
