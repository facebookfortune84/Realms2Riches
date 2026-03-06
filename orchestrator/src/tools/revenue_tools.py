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
    """
    Autonomously generates high-conversion landing pages.
    Pass 15: A/B Testing, Pixel Tracking, and SEO Hardening.
    """
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        params = invocation.input_data or {}
        product_name = params.get("product_name", "Jarvis 3.5")
        stripe_url = params.get("checkout_url", "https://buy.stripe.com/5kQcN5aHLdIdbAS4dd8so02")
        variant = random.choice(["Control", "Aggressive", "Scarcity"])
        
        # UX Reconstruction: Dynamic HTML Template with Tracking
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{product_name} | Sovereign Intelligence (Variant: {variant})</title>
            <script>
                function trackClick(e) {{
                    fetch('/api/v1/telemetry/click', {{
                        method: 'POST',
                        body: JSON.stringify({{ variant: '{variant}', product: '{product_name}' }})
                    }});
                }}
            </script>
            <style>
                body {{ font-family: 'Inter', sans-serif; background: #050505; color: #fff; padding: 100px; text-align: center; }}
                .glass-card {{ border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.05); padding: 60px; border-radius: 20px; backdrop-filter: blur(10px); }}
                h1 {{ font-size: 48px; background: linear-gradient(90deg, #00ff00, #008000); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
                .cta-btn {{ background: #00ff00; color: #000; padding: 20px 40px; text-decoration: none; font-weight: 900; border-radius: 50px; font-size: 20px; transition: 0.3s; }}
                .cta-btn:hover {{ box-shadow: 0 0 30px #00ff00; transform: scale(1.05); }}
            </style>
        </head>
        <body>
            <div class="glass-card">
                <p style="color: #00ff00;">>>> SOVEREIGN NODE INITIALIZED <<<</p>
                <h1>{product_name}</h1>
                <p>Variant: {variant} | Conversion Protocol Active.</p>
                <br><br>
                <a href="{stripe_url}" class="cta-btn" onclick="trackClick()">CLAIM YOUR SOVEREIGN LICENSE</a>
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
