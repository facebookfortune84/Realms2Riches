import json
import os
import stripe
import random
from datetime import datetime
from typing import Dict, Any, List
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.validation.schemas import ToolInvocation
from orchestrator.src.core.config import settings
from orchestrator.src.core.catalog.api import catalog_api
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
    def execute(self, invocation: Any) -> Dict[str, Any]:
        params = invocation if isinstance(invocation, dict) else (invocation.input_data or {})
        product_id = params.get("id")
        if not product_id:
            return {"status": "error", "reason": "Missing product id"}
            
        output_dir = "data/store/slots"
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{product_id}.json")
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(params, f, indent=2)
            
        logger.info(f"Product Forge: Created {file_path}")
        return {"status": "success", "artifact": file_path}

class PaymentTool(BaseTool):
    def execute(self, invocation: Any) -> Dict[str, Any]:
        params = invocation if isinstance(invocation, dict) else (invocation.input_data or {})
        email = params.get("email")
        product_id = params.get("product_id")
        
        # Real Stripe Integration
        if not settings.STRIPE_API_KEY or settings.STRIPE_API_KEY == "placeholder":
             return {"status": "skipped", "reason": "No Stripe key"}
             
        try:
            stripe.api_key = settings.STRIPE_API_KEY
            # Simplified checkout link generation or session creation
            # In production, this would create a checkout session
            return {
                "status": "success", 
                "checkout_url": f"https://checkout.stripe.com/pay/{product_id}?prefilled_email={email}"
            }
        except Exception as e:
            return {"status": "error", "reason": str(e)}

class YieldAuditorTool(BaseTool):
    def execute(self, invocation: Any) -> Dict[str, Any]:
        # Implementation of TMR calculation
        # Scan products and simulated conversion rates
        try:
            products = catalog_api.get_products()
            logger.info(f"Auditor: Found {len(products)} products.")
            total_potential = sum([p.prices[0].price for p in products if p.prices]) * 0.05 * 30 # Mock math
            
            return {
                "status": "success",
                "theoretical_monthly_runrate": total_potential,
                "product_count": len(products),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Auditor Error: {e}")
            return {"status": "error", "reason": str(e)}

def get_revenue_tools() -> List[BaseTool]:
    cfg = {"type": "object", "properties": {"product_name": {"type": "string"}}}
    return [
        SalesFunnelTool(ToolConfig(tool_id="sales_funnel", name="Funnel", description="Funnel Generator", parameters_schema=cfg, allowed_agents=["*"])),
        ProductForgeTool(ToolConfig(tool_id="product_forge", name="Forge", description="Product Forge", parameters_schema=cfg, allowed_agents=["*"])),
        PaymentTool(ToolConfig(tool_id="payment", name="Payment", description="Payment", parameters_schema={}, allowed_agents=["*"])),
        YieldAuditorTool(ToolConfig(tool_id="auditor", name="Auditor", description="Yield Auditor", parameters_schema={}, allowed_agents=["*"]))
    ]
