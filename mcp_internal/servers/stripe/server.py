import logging
from mcp.server.fastmcp import FastMCP
from orchestrator.src.tools.revenue_tools import (
    PaymentTool, 
    SalesFunnelTool,
    YieldAuditorTool,
    ProfitOracleTool,
    NicheLanderEngine,
    AffiliateTrackerTool,
    TieredBillingTool,
    ProfitCalculatorTool
)
from orchestrator.src.tools.base import ToolConfig

import sys
# Configure logging to stderr (stdout is for JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("mcp-stripe")

# Initialize FastMCP Server
mcp = FastMCP("Realms2Riches Stripe Server")

# Helper to init tools (since they require config)
def _get_tool(cls, name):
    return cls(ToolConfig(
        tool_id=name.lower(),
        name=name,
        description=f"MCP Wrapper for {name}",
        parameters_schema={},
        allowed_agents=["*"]
    ))

@mcp.tool()
async def create_payment_link(email: str, product_id: str) -> str:
    """Create a Stripe payment link for a product."""
    tool = _get_tool(PaymentTool, "Payment")
    result = tool.execute({"email": email, "product_id": product_id})
    return str(result)

@mcp.tool()
async def generate_sales_funnel(product_name: str, checkout_url: str) -> str:
    """Generate a sales funnel HTML page."""
    tool = _get_tool(SalesFunnelTool, "SalesFunnel")
    result = tool.execute({"product_name": product_name, "checkout_url": checkout_url})
    return str(result)

@mcp.tool()
async def audit_yield() -> str:
    """Audit current yield and runrate."""
    tool = _get_tool(YieldAuditorTool, "YieldAuditor")
    result = tool.execute({})
    return str(result)

@mcp.tool()
async def get_profit_report() -> str:
    """Get net profit report and system mood."""
    tool = _get_tool(ProfitOracleTool, "ProfitOracle")
    result = tool.execute({})
    return str(result)

@mcp.tool()
async def generate_niche_landers() -> str:
    """Generate programmatic SEO landers."""
    tool = _get_tool(NicheLanderEngine, "NicheEngine")
    result = tool.execute({})
    return str(result)

@mcp.tool()
async def track_affiliate(affiliate_id: str, action: str = "track_click") -> str:
    """Track an affiliate action."""
    tool = _get_tool(AffiliateTrackerTool, "AffiliateTracker")
    result = tool.execute({"affiliate_id": affiliate_id, "action": action})
    return str(result)

@mcp.tool()
async def upgrade_user_tier(user_id: str, target_tier: str) -> str:
    """Upgrade a user's billing tier."""
    tool = _get_tool(TieredBillingTool, "TieredBilling")
    result = tool.execute({"user_id": user_id, "target_tier": target_tier})
    return str(result)

@mcp.tool()
async def calculate_roi(industry: str, leads_per_month: float, avg_deal_value: float) -> str:
    """Calculate ROI projection."""
    tool = _get_tool(ProfitCalculatorTool, "ProfitCalculator")
    result = tool.execute({
        "industry": industry,
        "leads_per_month": leads_per_month,
        "avg_deal_value": avg_deal_value
    })
    return str(result)

if __name__ == "__main__":
    mcp.run()
