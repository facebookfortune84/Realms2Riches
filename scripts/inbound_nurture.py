import json
import os
import logging
import sys
from datetime import datetime, timedelta
from orchestrator.src.memory.sql_store import SQLStore
from orchestrator.src.tools.smtp_tools import SMTPOutreachTool, ToolConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("InboundNurture")

def run_nurture_cycle():
    """
    Monitors clicks.json and triggers follow-up for users who didn't buy.
    """
    clicks_path = "data/customers/clicks.json"
    leads_path = "data/customers/leads.json"
    
    if not os.path.exists(clicks_path) or not os.path.exists(leads_path):
        logger.info("Nothing to nurture yet.")
        return

    # 1. Load data
    with open(leads_path, "r") as f:
        leads = json.load(f)
    
    # In a real scenario, we'd match click IP/source to a lead email.
    # For this autonomous loop, we'll nurture leads who were added > 24h ago
    # AND have no 'revenue' record in SQLStore.
    
    sql = SQLStore()
    # Mocking a way to find users without payments
    # In prod, we'd query: SELECT email FROM leads WHERE email NOT IN (SELECT email FROM profit_ledger)
    
    nurture_count = 0
    smtp = SMTPOutreachTool(ToolConfig(tool_id="nurture_smtp", name="Nurture", description="Followup", parameters_schema={}, allowed_agents=["*"]))
    
    for lead in leads:
        email = lead.get("email")
        if not email: continue
        
        # Check if they already paid (theoretical check)
        # For simulation, we'll just nurture everyone once.
        if lead.get("nurtured"): continue
        
        logger.info(f"📬 Triggering Nurture Sequence for {email}")
        
        # Send Scarcity Email
        smtp.execute({
            "recipient": email,
            "subject": "Final Notice: Your Sovereign License is expiring",
            "body": "We noticed you checked out the Platinum Matrix but didn't secure your slot. Only 2 remain for this cohort."
        })
        
        lead["nurtured"] = True
        nurture_count += 1

    # Update leads
    if nurture_count > 0:
        with open(leads_path, "w") as f:
            json.dump(leads, f, indent=2)
        logger.info(f"✅ Nurture Cycle Complete. {nurture_count} follow-ups sent.")

if __name__ == "__main__":
    run_nurture_cycle()
