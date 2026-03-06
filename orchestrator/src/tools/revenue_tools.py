import json
import os
import stripe
from typing import Dict, Any, List
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.validation.schemas import ToolInvocation
from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class SalesFunnelTool(BaseTool):
    """
    Autonomously generates high-conversion landing pages.
    Reconstructs the customer journey with dynamic CTAs and SEO hooks.
    """
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        params = invocation.input_data or {}
        product_name = params.get("product_name", "Jarvis 3.5")
        stripe_url = params.get("checkout_url", "https://buy.stripe.com/5kQcN5aHLdIdbAS4dd8so02")
        theme = params.get("theme", "Sovereign Industrial")
        
        # UX Reconstruction: Dynamic HTML Template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{product_name} | Sovereign Intelligence</title>
            <style>
                body {{ font-family: 'Courier New', Courier, monospace; background: #0a0a0a; color: #00ff00; padding: 50px; text-align: center; }}
                .container {{ border: 1px solid #00ff00; padding: 40px; display: inline-block; max-width: 600px; }}
                h1 {{ letter-spacing: 5px; text-transform: uppercase; }}
                .cta-btn {{ background: #00ff00; color: #000; padding: 15px 30px; text-decoration: none; font-weight: bold; border-radius: 5px; }}
                .seo-text {{ color: #555; font-size: 10px; margin-top: 50px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{product_name}</h1>
                <p>Status: ARCHITECT INITIALIZED</p>
                <p>You have been identified as a high-value node. Access the Sovereign Intelligence Unit now.</p>
                <br><br>
                <a href="{stripe_url}" class="cta-btn">INITIALIZE CONVERSION</a>
            </div>
            <div class="seo-text">
                Keywords: Autonomous agents, Jarvis 3.5, Revenue Orchestration, Sovereign Tech
            </div>
        </body>
        </html>
        """
        
        output_dir = "projects/generated/landers"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{product_name.lower().replace(' ', '_')}_lander.html"
        file_path = os.path.join(output_dir, filename)
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            logger.info(f"UX Reconstruction: Generated lander for {product_name} at {file_path}")
            return {
                "status": "success",
                "lander_url": f"/landers/{filename}",
                "product": product_name,
                "conversion_point": stripe_url
            }
        except Exception as e:
            return {"status": "error", "reason": str(e)}

class ProductForgeTool(BaseTool):
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        params = invocation.input_data or {}
        product_id = params.get("id", "new_slot")
        name = params.get("name", "Titan Forge")
        price = params.get("price", 499)
        description = params.get("description", "Modular revenue agent.")
        
        slot_data = {
            "id": product_id, "name": name, "price": price, 
            "description": description, 
            "stripe_link": "https://buy.stripe.com/5kQcN5aHLdIdbAS4dd8so02"
        }
        
        file_path = f"data/store/slots/{product_id}.json"
        os.makedirs("data/store/slots", exist_ok=True)
        try:
            with open(file_path, "w") as f:
                json.dump(slot_data, f, indent=2)
            return {"status": "success", "artifact": file_path}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

def get_revenue_tools() -> List[BaseTool]:
    base_cfg = {"type": "object", "properties": {"product_name": {"type": "string"}}}
    return [
        SalesFunnelTool(ToolConfig(tool_id="sales_funnel", name="Funnel Architect", description="Generates landers", parameters_schema=base_cfg, allowed_agents=["*"])),
        ProductForgeTool(ToolConfig(tool_id="product_forge", name="Product Forge", description="Creates revenue slots", parameters_schema=base_cfg, allowed_agents=["*"]))
    ]
