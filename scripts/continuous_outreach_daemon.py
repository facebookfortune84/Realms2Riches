import asyncio
import os
import sys
import json
import random
import time
import subprocess # For launching extraction swarm
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.future import select
from arq import create_pool
from arq.connections import RedisSettings

# Ensure imports work
sys.path.append(os.getcwd())

from orchestrator.src.validation.schemas import ToolInvocation, LeadStatus # Import LeadStatus
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.core.database import AsyncSessionLocal
from orchestrator.src.core.models import Lead # Import Lead model
from orchestrator.src.core.config import settings
from orchestrator.src.tools.marketing_tools import get_marketing_tools

logger = get_logger("OUTREACH_DAEMON")

SLEEP_INTERVAL = 30 # Check for new tasks every 30 seconds

class ContinuousOutreachDaemon:
    def __init__(self):
        self.marketing_tools = {t.config.tool_id: t for t in get_marketing_tools()}
        self.high_ticket_partners = self._load_high_ticket()

    def _load_high_ticket(self) -> List[Dict]:
        path = "data/catalog/high_ticket_affiliates.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return []

    async def generate_email_content(self, lead: Lead) -> str:
        """Generates personalized email content using marketing tools and high-ticket partners."""
        try:
            name = lead.first_name or "Founder"
            company = lead.company or "your company"
            
            # Extract relevant context for personalization
            scraped_text_context = " ".join(lead.meta_data.get("scraped_text", []))
            company_desc = lead.meta_data.get('description', 'innovative company')
            
            # --- High-Ticket Affiliate Strategy ---
            # Simple keyword matching for now, could be enhanced with LLM
            niche_keywords = [p['niche'].lower() for p in self.high_ticket_partners]
            matched_niche = next((nk for nk in niche_keywords if nk in scraped_text_context.lower()), None)
            
            partner = None
            if matched_niche:
                partner = next((p for p in self.high_ticket_partners if p["niche"].lower() == matched_niche), None)
            
            if partner:
                logger.info(f"🎯 Matching {company} with High-Ticket Partner: {partner['name']}")
                return f"""
                <html>
                <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
                    <p>Hi {name},</p>
                    <p>I noticed {company}'s work in the {partner['niche']} space. I believe you'd find significant value in a specialized solution we've partnered with.</p>
                    <p>We're offering exclusive access to <strong>{partner['name']}</strong>'s {partner['niche']} framework, a {partner['price']} system designed to elevate {partner['niche']} operations.</p>
                    <p>{partner['description']}</p>
                    <p>Learn more and see if it aligns with your goals: <a href="{partner['link']}" style="color: #007bff; text-decoration: none; font-weight: bold;">Partner Integration Details</a></p>
                    <p>Best,<br>Robert DeMotto<br>Realms2Riches</p>
                </body>
                </html>
                """

            # --- Standard Content Generation ---
            if "email_gen" in self.marketing_tools:
                res = await asyncio.to_thread(
                    self.marketing_tools["email_gen"].execute, 
                    ToolInvocation(
                        tool_id="email_gen",
                        input_data={
                            "product_name": settings.PRODUCT_NAME,
                            "target_audience": f"{name} at {company}",
                            "key_benefits": "Autonomous Revenue Generation, AI Workforce, 24/7 Operations",
                            "company_description": company_desc,
                            "scraped_context": scraped_text_context
                        },
                        agent_id="daemon"
                    )
                )
                if res.get("status") == "success":
                    return res.get("email_content")
            
            # Fallback template if no tools or tools fail
            return f"""
            <html>
            <body>
                <p>Hi {name},</p>
                <p>I'm reaching out because I've been following {company}'s progress.</p>
                <p>We've developed an advanced autonomous AI system, the <strong>{settings.PRODUCT_NAME}</strong>, that handles complex operations for businesses like yours.</p>
                <p>Would you be open to a brief exploration of how this could automate your processes and boost revenue?</p>
                <p>Best,<br>Robert DeMotto<br>Founder, {settings.BRAND_NAME}</p>
                <p><a href="{settings.MARKETING_SITE_URL}">Learn More</a></p>
            </body>
            </html>
            """
        except Exception as e:
            logger.error(f"Error generating email content: {e}")
            return "Error generating content."

    async def run(self):
        logger.info("🚀 CONTINUOUS OUTREACH DAEMON STARTED (POSTGRES + REDIS)")
        
        # Connect to Redis for task enqueuing
        redis = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL or "redis://localhost:6379"))

        while True:
            async with AsyncSessionLocal() as session:
                # 1. Fetch leads ready for enrichment/outreach
                # Fetch leads that are SCRAPED and ready to be processed
                stmt = select(Lead).where(Lead.status == LeadStatus.SCRAPED).limit(20) # Fetch up to 20 leads at a time
                result = await session.execute(stmt)
                leads_to_process = result.scalars().all()
                
                # REPLENISHMENT: If leads are low, trigger extraction swarm
                if len(leads_to_process) < 5:
                    logger.info("⚠️ Leads queue is low. Triggering recursive lead extraction swarm...")
                    try:
                        # Launch extraction script as a separate process to avoid blocking
                        subprocess.Popen([sys.executable, "scripts/lead_extraction_swarm.py"],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                        logger.info("👍 Lead extraction swarm initiated.")
                    except Exception as e:
                        logger.error(f"Failed to launch lead extraction swarm: {e}")

                if not leads_to_process:
                    logger.info("💤 No leads in SCRAPED status. Sleeping...")
                else:
                    for lead in leads_to_process:
                        logger.info(f"🚀 Enqueuing enrichment/outreach for: {lead.email} ({lead.company})")
                        
                        # Enqueue the enrichment task which will lead to personalized outreach
                        await redis.enqueue_job('scrape_enrich_task', lead_id=lead.id)
                        
                        # Update lead status to QUEUED to prevent re-processing by this daemon
                        lead.status = LeadStatus.QUEUED
                        session.add(lead)
                    
                    await session.commit()
                    logger.info(f"✅ Enqueued {len(leads_to_process)} leads into the Sovereign Intelligence Queue.")

            await asyncio.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    daemon = ContinuousOutreachDaemon()
    try:
        asyncio.run(daemon.run())
    except KeyboardInterrupt:
        logger.info("🛑 Daemon Stopped.")
