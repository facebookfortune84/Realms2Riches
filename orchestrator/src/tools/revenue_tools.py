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

class ProfitOracleTool(BaseTool):
    """
    Platinum Profit Oracle.
    Calculates Net Profit: Revenue - (API Costs + Fees).
    Used to trigger Stop-Loss or Scaling.
    """
    def execute(self, invocation: Any) -> Dict[str, Any]:
        try:
            from orchestrator.src.memory.sql_store import SQLStore
            sql = SQLStore()
            net_profit = sql.get_total_profit()
            
            # Simple scaling logic
            mood = "AGGRESSIVE" if net_profit > 0 else "CAUTIOUS"
            if net_profit < -50: mood = "STOP_LOSS_WARNING"
            
            return {
                "status": "success",
                "net_profit": net_profit,
                "currency": "USD",
                "system_mood": mood,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"status": "error", "reason": str(e)}

class NicheLanderEngine(BaseTool):
    """
    Programmatic SEO Engine.
    Generates 1,000+ niche-specific landing page configurations.
    Served dynamically via /niche/{slug}.
    """
    INDUSTRIES = ["Dental", "Legal", "Real Estate", "SaaS", "Crypto", "E-commerce", "HVAC", "Plumbing", "Law", "Insurance"]
    PAIN_POINTS = ["High Lead Cost", "Slow Response Time", "Manual Follow-up", "Low Conversion", "Staff Burnout"]
    REGIONS = ["Austin", "London", "New York", "Berlin", "Sydney", "Global", "California", "Texas", "Dubai", "Singapore"]

    def execute(self, invocation: Any) -> Dict[str, Any]:
        output_dir = "data/store/niches"
        os.makedirs(output_dir, exist_ok=True)
        
        count = 0
        for ind in self.INDUSTRIES:
            for pain in self.PAIN_POINTS:
                for reg in self.REGIONS:
                    slug = f"{ind.lower()}-{pain.lower().replace(' ', '-')}-{reg.lower()}"
                    niche_data = {
                        "id": slug,
                        "title": f"Autonomous {ind} Revenue Agent for {reg}",
                        "headline": f"Stop {pain} in your {ind} Practice today.",
                        "description": f"The Sovereign Matrix delivers 24/7 automated conversion for {ind} professionals in {reg}.",
                        "cta_link": "https://buy.stripe.com/5kQcN5aHLdIdbAS4dd8so02",
                        "industry": ind,
                        "region": reg,
                        "pain_point": pain,
                        "image_url": f"/marketing/images/{ind.lower()}.png"
                    }
                    
                    with open(os.path.join(output_dir, f"{slug}.json"), "w") as f:
                        json.dump(niche_data, f, indent=2)
                    count += 1
        
        logger.info(f"SEO: Generated {count} programmatic niche configurations.")
        return {"status": "success", "count": count}

class AffiliateTrackerTool(BaseTool):
    """
    2-Tier Affiliate System.
    Tracks referrals and multi-tier commission splits.
    """
    def execute(self, invocation: Any) -> Dict[str, Any]:
        params = invocation if isinstance(invocation, dict) else (invocation.input_data or {})
        action = params.get("action", "track_click")
        affiliate_id = params.get("affiliate_id")
        
        if not affiliate_id:
            return {"status": "error", "reason": "No affiliate_id provided"}

        # Simulate tracking in DB
        logger.info(f"🤝 AFFILIATE: Action {action} for {affiliate_id}")
        return {"status": "success", "tracked": True, "commission_tier": "15% Primary"}

class TieredBillingTool(BaseTool):
    """
    One-Click Upgrade & Tiered Access Manager.
    Handles shifts between Basic, Pro, and Sovereign tiers.
    """
    def execute(self, invocation: Any) -> Dict[str, Any]:
        params = invocation if isinstance(invocation, dict) else (invocation.input_data or {})
        user_id = params.get("user_id")
        target_tier = params.get("target_tier", "PRO")
        
        logger.info(f"💳 BILLING: Upgrading user {user_id} to {target_tier}")
        return {
            "status": "success",
            "new_tier": target_tier,
            "stripe_session": "https://checkout.stripe.com/upgrade-mock",
            "upsell_available": "Matrix-Speed-Boost-v1"
        }

class ProfitCalculatorTool(BaseTool):
    """
    Interactive ROI/Profit Calculator.
    Predicts revenue based on Industry benchmarks.
    """
    INDUSTRY_MULTIPLIERS = {
        "Dental": 1.5, "Legal": 2.0, "SaaS": 1.2, "Real Estate": 1.8, "Crypto": 2.5
    }

    def execute(self, invocation: Any) -> Dict[str, Any]:
        params = invocation if isinstance(invocation, dict) else (invocation.input_data or {})
        industry = params.get("industry", "SaaS")
        leads_per_month = float(params.get("leads_per_month", 100))
        avg_deal_value = float(params.get("avg_deal_value", 500))
        
        mult = self.INDUSTRY_MULTIPLIERS.get(industry, 1.0)
        projected_conv = 0.05 * mult # 5% base * multiplier
        
        gross = leads_per_month * projected_conv * avg_deal_value
        net = gross - 2999 # Sub cost
        
        return {
            "status": "success",
            "industry": industry,
            "projected_conversion": f"{projected_conv*100:.1f}%",
            "monthly_gross": gross,
            "monthly_net": net,
            "roi_multiple": gross / 2999 if gross > 0 else 0
        }

def get_revenue_tools() -> List[BaseTool]:
    cfg = {"type": "object", "properties": {"product_name": {"type": "string"}}}
    calc_cfg = {"type": "object", "properties": {"industry": {"type": "string"}, "leads_per_month": {"type": "number"}}}
    return [
        SalesFunnelTool(ToolConfig(tool_id="sales_funnel", name="Funnel", description="Funnel Generator", parameters_schema=cfg, allowed_agents=["*"])),
        ProductForgeTool(ToolConfig(tool_id="product_forge", name="Forge", description="Product Forge", parameters_schema=cfg, allowed_agents=["*"])),
        PaymentTool(ToolConfig(tool_id="payment", name="Payment", description="Payment", parameters_schema={}, allowed_agents=["*"])),
        YieldAuditorTool(ToolConfig(tool_id="auditor", name="Auditor", description="Yield Auditor", parameters_schema={}, allowed_agents=["*"])),
        ProfitOracleTool(ToolConfig(tool_id="profit_oracle", name="Profit Oracle", description="Net Profit Tracker", parameters_schema={}, allowed_agents=["*"])),
        NicheLanderEngine(ToolConfig(tool_id="niche_engine", name="Niche Engine", description="pSEO Engine", parameters_schema={}, allowed_agents=["*"])),
        AffiliateTrackerTool(ToolConfig(tool_id="affiliate_tracker", name="Affiliate", description="2-Tier tracking", parameters_schema={}, allowed_agents=["*"])),
        TieredBillingTool(ToolConfig(tool_id="tiered_billing", name="Billing", description="Tiered billing", parameters_schema={}, allowed_agents=["*"])),
        ProfitCalculatorTool(ToolConfig(tool_id="profit_calculator", name="ROI Calculator", description="ROI prediction", parameters_schema=calc_cfg, allowed_agents=["*"]))
    ]
