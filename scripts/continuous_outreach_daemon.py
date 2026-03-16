import asyncio
import os
import sys
import json
import random
import time
from datetime import datetime
from typing import List, Dict, Any

# Ensure imports work
sys.path.append(os.getcwd())

from orchestrator.src.validation.schemas import ToolInvocation
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.tools.smtp_tools import get_smtp_tools
from orchestrator.src.tools.marketing_tools import get_marketing_tools

logger = get_logger("OUTREACH_DAEMON")

LEADS_FILE = "data/customers/leads.json"
LOG_FILE = "data/marketing/outreach_log.json"
SLEEP_INTERVAL = 300  # 5 minutes

class ContinuousOutreachDaemon:
    def __init__(self):
        self.smtp_tool = {t.config.tool_id: t for t in get_smtp_tools()}["smtp_outreach"]
        self.marketing_tools = {t.config.tool_id: t for t in get_marketing_tools()}
        self.sent_log = self._load_log()
        self.high_ticket_partners = self._load_high_ticket()

    def _load_high_ticket(self) -> List[Dict]:
        path = "data/catalog/high_ticket_affiliates.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return []

    def _load_log(self) -> List[str]:
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_log(self):
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "w") as f:
            json.dump(self.sent_log, f, indent=2)

    def _load_leads(self) -> List[Dict]:
        if os.path.exists(LEADS_FILE):
            try:
                with open(LEADS_FILE, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    async def generate_email_content(self, lead: Dict) -> str:
        """Generates personalized email content using marketing tools and high-ticket partners."""
        try:
            name = lead.get("name", "Founder")
            company = lead.get("company", "your company")
            niche = (lead.get("niche") or lead.get("description") or "").lower()
            
            # Match niche with high-ticket partner
            partner = next((p for p in self.high_ticket_partners if p["niche"].lower() in niche), None)
            
            if partner:
                logger.info(f"🎯 Matching {name} with High-Ticket Partner: {partner['name']}")
                return f"""
                <html><body>
                    <p>Hi {name},</p>
                    <p>I saw your work at {company} and thought you'd be interested in a specialized breakthrough.</p>
                    <p>Beyond our autonomous systems, we've partnered with <b>{partner['name']}</b> ({partner['creator']}) to offer exclusive access to their {partner['price']} {partner['niche']} framework.</p>
                    <p>{partner['description']}</p>
                    <p>You can review the integration here: <a href="{partner['link']}">Partner Uplink</a></p>
                    <p>Best,<br>Robert DeMotto</p>
                </body></html>
                """

            # Use 'email_gen' tool to create dynamic content
            if "email_gen" in self.marketing_tools:
                res = await asyncio.to_thread(
                    self.marketing_tools["email_gen"].execute, 
                    ToolInvocation(
                        tool_id="email_gen",
                        input_data={
                            "product_name": "Realms2Riches Industrial Matrix",
                            "target_audience": f"{name} at {company}",
                            "key_benefits": "Autonomous Revenue Generation, AI Workforce, 24/7 Operations"
                        },
                        agent_id="daemon"
                    )
                )
                if res.get("status") == "success":
                    return res.get("email_content")
            
            # Fallback template
            return f"""
            <html>
            <body>
                <p>Hi {name},</p>
                <p>I noticed {company} is innovating in the tech space. I wanted to share a breakthrough in autonomous revenue generation.</p>
                <p><b>Realms2Riches</b> is an industrial-grade AI matrix that autonomously manages marketing, sales, and operations.</p>
                <p>We are currently onboarding select partners. Would you be open to a 5-minute demo?</p>
                <p>Best,<br>Robert DeMotto<br>Founder, Realms2Riches</p>
                <p><a href="https://realmstoriches.xyz">View the System</a></p>
            </body>
            </html>
            """
        except Exception as e:
            logger.error(f"Error generating email: {e}")
            return "Error generating content."

    async def run(self):
        logger.info("🚀 CONTINUOUS OUTREACH DAEMON STARTED")
        
        while True:
            leads = self._load_leads()
            new_leads = [l for l in leads if l.get("email") and l["email"] not in self.sent_log]
            
            # RECURSIVE REPLENISHMENT: Trigger extraction if leads are low
            if len(new_leads) < 20:
                logger.info("⚠️ Leads running low. Triggering recursive lead extraction...")
                try:
                    import subprocess
                    subprocess.Popen([sys.executable, "scripts/lead_extraction_swarm.py"], 
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception as e:
                    logger.error(f"Replenishment failed: {e}")

            if not new_leads:
                logger.info("💤 No new leads found. Sleeping...")
            else:
                # Process one lead per cycle to be safe
                target = random.choice(new_leads)
                email = target["email"]
                logger.info(f"📧 Targeting: {email} ({target.get('name')})")
                
                content = await self.generate_email_content(target)
                
                try:
                    result = await asyncio.to_thread(
                        self.smtp_tool.execute,
                        ToolInvocation(
                            tool_id="smtp_outreach",
                            input_data={
                                "target_email": email,
                                "subject": f"Autonomous Revenue for {target.get('name', 'You')}",
                                "html_body": content
                            },
                            agent_id="daemon"
                        )
                    )
                    
                    if result.get("status") == "success":
                        logger.info(f"✅ Email Sent to {email}")
                        self.sent_log.append(email)
                        self._save_log()
                    else:
                        logger.error(f"❌ Failed to send to {email}: {result.get('reason')}")
                        
                except Exception as e:
                    logger.error(f"❌ Exception sending to {email}: {e}")

            await asyncio.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    daemon = ContinuousOutreachDaemon()
    try:
        asyncio.run(daemon.run())
    except KeyboardInterrupt:
        logger.info("🛑 Daemon Stopped.")
