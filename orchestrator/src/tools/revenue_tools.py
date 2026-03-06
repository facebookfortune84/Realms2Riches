import json
import os
import stripe
import random
from typing import Dict, Any, List
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.validation.schemas import ToolInvocation
from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class SalesFunnelTool(BaseTool):
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        params = invocation.input_data or {}
        product_name = params.get("product_name", "Jarvis 3.5")
        stripe_url = params.get("checkout_url", "https://buy.stripe.com/5kQcN5aHLdIdbAS4dd8so02")
        variant = random.choice(["Control", "Aggressive", "Scarcity"])
        
        html_content = f"<html><title>{product_name} | Variant: {variant}</title><body><h1>{product_name}</h1><a href='{stripe_url}'>Buy Now</a></body></html>"
        output_dir = "projects/generated/landers"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{product_name.lower().replace(' ', '_')}_lander.html"
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        logger.info(f"UX: Generated lander at {file_path}")
        return {"status": "success", "lander_url": f"/landers/{filename}", "artifact": file_path}

class ProductForgeTool(BaseTool):
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        return {"status": "success"}

class PaymentTool(BaseTool):
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        return {"status": "success"}

class YieldAuditorTool(BaseTool):
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        return {"status": "success"}

def get_revenue_tools() -> List[BaseTool]:
    cfg = {"type": "object", "properties": {"product_name": {"type": "string"}}}
    return [
        SalesFunnelTool(ToolConfig(tool_id="sales_funnel", name="Funnel", description="Funnel Generator", parameters_schema=cfg, allowed_agents=["*"])),
        ProductForgeTool(ToolConfig(tool_id="product_forge", name="Forge", description="Product Forge", parameters_schema=cfg, allowed_agents=["*"])),
        PaymentTool(ToolConfig(tool_id="payment", name="Payment", description="Payment", parameters_schema={}, allowed_agents=["*"])),
        YieldAuditorTool(ToolConfig(tool_id="auditor", name="Auditor", description="Yield Auditor", parameters_schema={}, allowed_agents=["*"]))
    ]
