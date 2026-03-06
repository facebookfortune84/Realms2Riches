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
    targets_path = "data/customers/yc_targets.json"
    if not os.path.exists(targets_path):
        logger.error(f"❌ Targets file missing: {targets_path}")
        return

    with open(targets_path, 'r', encoding='utf-8') as f:
        targets = json.load(f)

    logger.info(f"Step 1: Loaded {len(targets)} high-value targets.")
    
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

    # We'll process a small batch first to verify the pipeline
    test_batch = targets[:5]
    
    for target in test_batch:
        name = target.get("name")
        desc = target.get("description")
        
        # In a real scenario, we'd find the email. For now, we use the fallback or a placeholder.
        # The user mentioned robertdemottojr83@gmail.com is the sender.
        # We'll send a test to robertdemottojr50@gmail.com (the contact email in settings)
        target_email = settings.CONTACT_EMAIL 
        
        logger.info(f"🚀 Dispatching pitch to {name} (via {target_email})")
        
        # Load available personas to inject variety
        from orchestrator.src.agents.persona_library import PERSONA_LIBRARY
        persona_id = random.choice(list(PERSONA_LIBRARY.keys()))
        
        task_desc = f"As {persona_id}, use smtp_outreach to send a Jarvis 3.5 pitch to {target_email} for {name}. Description: {desc}. HTML Body: {get_pitch(name, desc)}"
        
        async for step in orchestrator.submit_task_stream(task_desc, "yc_outreach"):
            if step["status"] == "completed":
                logger.info(f"✅ Pitch sent to {name}")
            elif step["status"] == "failed":
                logger.error(f"❌ Failed for {name}: {step['reason']}")

    logger.info("🏁 SWARM EXECUTION COMPLETE.")

if __name__ == "__main__":
    asyncio.run(run_yc_outreach_swarm())
