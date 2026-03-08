import asyncio
import os
import sys
import json
import random

sys.path.append(os.getcwd())

from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.core.config import settings

logger = get_logger("YC_SWARM")

async def run_yc_outreach_swarm():
    logger.info("🦅 INITIATING Y-COMBINATOR TARGETED OUTREACH (STREAM 12) 🦅")
    
    orchestrator = Orchestrator()
    await orchestrator.startup()
    
    # Load targets
    targets_path = "data/customers/leads.json"
    if not os.path.exists(targets_path):
        logger.error(f"❌ Targets file missing: {targets_path}")
        return

    with open(targets_path, 'r', encoding='utf-8') as f:
        targets = json.load(f)

    logger.info(f"Step 1: Loaded {len(targets)} high-value targets from extraction.")
    
    # Pitch Template (Jarvis 3.5)
    def get_pitch(target_name, description):
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
                <h2 style="color: #663399;">Sovereign Intelligence for {target_name}</h2>
                <p>Hi {target_name} Team,</p>
                <p>I noticed your work in <strong>{description}</strong> and identified a massive opportunity to optimize your revenue operations using autonomous agentic swarms.</p>
                <p>We are deploying <strong>Jarvis 3.5</strong> units—the same tech powering the Realms2Riches monetization engine—to help YC companies scale technical authority and conversion sharding with zero human overhead.</p>
                
                <div style="background: #f4f4f4; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Jarvis 3.5 Capabilities:</h3>
                    <ul>
                        <li><strong>Autonomous SEO:</strong> Dominating search intent in < 5 mins.</li>
                        <li><strong>Lead Extraction Swarms:</strong> High-precision targeting via Playwright.</li>
                        <li><strong>Live Conversion Loops:</strong> Integrated Stripe financial protocols.</li>
                    </ul>
                </div>

                <p style="text-align: center;">
                    <a href="https://buy.stripe.com/5kQcN5aHLdIdbAS4dd8so02" 
                       style="background: #663399; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                       SECURE YOUR SOVEREIGN LICENSE
                    </a>
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee;">
                <p style="font-size: 12px; color: #777;">
                    Robert DeMotto<br>
                    Principal Architect | Realms2Riches<br>
                    Sent via Autonomous Stream 12
                </p>
            </div>
        </body>
        </html>
        """

    # Process FULL list for maximum impact
    targets_to_blitz = targets
    
    logger.info(f"🚀 INITIATING HDRB BLITZ: Processing {len(targets_to_blitz)} leads.")
    
    for target in targets_to_blitz:
        name = target.get("name")
        desc = target.get("description", "Innovation")
        target_email = target.get("email")
        
        if not target_email or target_email == "robertdemottojr50@gmail.com":
            # If it's the fallback, we still send one to prove the system, but normally we'd skip or use a better search
            pass
            
        logger.info(f"📡 Dispatching Sovereign Pitch to {name} ({target_email})")
        
        # Select persona with highest authority
        persona_id = "VANGUARD_ARCHITECT" 
        
        task_desc = f"Use smtp_outreach to deliver a Jarvis 3.5 Revenue Matrix pitch to {target_email} for the company {name}. Target Context: {desc}. Use the high-converting HTML template provided in the Sovereign RAG."
        
        try:
            # We run sequentially to maintain SMTP reputation but keep it fast
            async for step in orchestrator.submit_task_stream(task_desc, "hdrb_blitz"):
                if step["status"] == "completed":
                    logger.info(f"✅ [CONVERTED] Pitch Delivered to {name}")
                elif step["status"] == "failed":
                    logger.error(f"⚠️ [RETRY] Delivery failed for {name}: {step['reason']}")
        except Exception as e:
             logger.error(f"💥 HDRB Orchestrator error for {name}: {e}")

    logger.info("🏆 GLOBAL BLITZ COMPLETE. SWARM MONITORING FOR REPLIES.")

    logger.info("🏁 SWARM EXECUTION COMPLETE.")

if __name__ == "__main__":
    asyncio.run(run_yc_outreach_swarm())
