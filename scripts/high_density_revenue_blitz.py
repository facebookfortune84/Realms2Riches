import asyncio
import os
import sys
import json
import re

sys.path.append(os.getcwd())

from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.logging.logger import get_logger

logger = get_logger("REVENUE_BLITZ")

async def run_revenue_blitz():
    logger.info("🔥 STARTING INDUSTRIAL REVENUE HARVEST 🔥")
    
    orchestrator = Orchestrator()
    await orchestrator.startup()
    
    # Industrial Scale: Multi-Sector Targeting
    # We are using specific query strings that yield personal/direct contact pages
    sectors = [
        {"name": "AI Startup Founders", "query": "site:crunchbase.com 'contact information' artificial intelligence founder email"},
        {"name": "E-commerce Owners", "query": "site:linkedin.com/in/ 'owner' 'shopify' 'contact me at'"},
        {"name": "SaaS Decision Makers", "query": "site:apollo.io/companies 'software as a service' founder email"}
    ]
    
    # Product Tiering: High-ticket focus
    # We alternate products to test conversion across price points
    products = ["digital_domination", "startup_accelerator", "jarvis_premium"]
    
    for i, sector in enumerate(sectors):
        logger.info(f"🚀 Deploying Swarm to Sector: {sector['name']}")
        
        # We instruct the agent to use Playwright to find REAL emails, not placeholders
        task_desc = (
            f"INDUSTRIAL MISSION: 1. Use the browser tool to search for: {sector['query']}. "
            f"2. Navigate the top 5 results and use your regex intelligence to extract REAL validated email addresses. "
            f"3. For every REAL email found, use the outreach tool to pitch the '{products[i % len(products)]}' package. "
            f"4. If you hit a login wall or captcha, immediately pivot to the next result. "
            f"5. MANDATORY: You must land at least 3 industrial pitches per sector."
        )
        
        async for step in orchestrator.submit_task_stream(task_desc, f"blitz_{i}"):
            if step["status"] == "completed":
                logger.info(f"✅ Sector {sector['name']} Blitz Node Synchronized.")
                results = step.get("result", {}).get("results", [])
                landed = [r for r in results if r.get("tool_id") == "outreach" and r.get("output_data", {}).get("status") == "success"]
                logger.info(f"📊 Industrial Yield: {len(landed)} Pitches Delivered to {sector['name']}.")
            elif step["status"] == "failed":
                logger.error(f"❌ Blitz Node Failure in {sector['name']}: {step['reason']}")

    logger.info("🏆 INDUSTRIAL HARVEST COMPLETE. REVENUE VECTORS ARE ACTIVE. 🏆")

if __name__ == "__main__":
    asyncio.run(run_revenue_blitz())
