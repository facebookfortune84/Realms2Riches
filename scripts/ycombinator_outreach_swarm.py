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

    # Process a batch to verify the pipeline
    test_batch = targets[:5]
    
    for target in test_batch:
        name = target.get("name")
        desc = target.get("description", "Innovation")
        target_email = target.get("email")
        
        if not target_email:
            logger.warning(f"⚠️ No email for {name}, skipping.")
            continue
            
        logger.info(f"🚀 Dispatching pitch to {name} ({target_email})")
        
        # Load available personas to inject variety
        from orchestrator.src.agents.persona_library import PERSONA_LIBRARY
        persona_id = random.choice(list(PERSONA_LIBRARY.keys()))
        
        # Note: orchestrator.submit_task_stream requires the tool to be available to the agent.
        # We assume the default agent or specific persona has 'smtp_outreach' tool.
        # If not, we might need to invoke the tool directly or ensure the agent has it.
        # But per the script structure, we use the orchestrator.
        
        task_desc = f"As {persona_id}, use smtp_outreach to send a Jarvis 3.5 pitch to {target_email} for {name}. Description: {desc}. HTML Body: {get_pitch(name, desc)}"
        
        try:
            async for step in orchestrator.submit_task_stream(task_desc, "yc_outreach"):
                if step["status"] == "completed":
                    logger.info(f"✅ Pitch sent to {name}")
                elif step["status"] == "failed":
                    logger.error(f"❌ Failed for {name}: {step['reason']}")
        except Exception as e:
             logger.error(f"Orchestrator error for {name}: {e}")

    logger.info("🏁 SWARM EXECUTION COMPLETE.")

    logger.info("🏁 SWARM EXECUTION COMPLETE.")

if __name__ == "__main__":
    asyncio.run(run_yc_outreach_swarm())
