import asyncio
import logging
import random
from typing import List, Dict, Any
from orchestrator.src.core.config import settings
from orchestrator.src.core.self_healing import sovereign_healer

logger = logging.getLogger(__name__)

class AutonomousBacklog:
    """
    Constant task generator for the Sovereign Swarm.
    Ensures agents are never idle and always working towards monetization.
    """
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.is_running = False

    async def start(self):
        self.is_running = True
        logger.info("⚙️ AUTONOMOUS BACKLOG GENERATOR ACTIVE.")
        while self.is_running:
            try:
                # 1. Analyze System Needs & Maintenance
                task_pool = [
                    "Perform a high-density lead extraction scrape for AI SaaS founders.",
                    "Audit the last 5 outreach emails for conversion sentiment.",
                    "Generate a viral TikTok script for the Sovereign Brand Kit.",
                    "Verify Stripe catalog alignment and price parity.",
                    "Generate a technical SEO breakdown for 'Autonomous Revenue Agents'."
                ]
                
                # INJECT MAINTENANCE BACKLOG
                maintenance = sovereign_healer.get_maintenance_tasks()
                if maintenance:
                    logger.info(f"🛠️ Backlog: Injected {len(maintenance)} maintenance tasks.")
                    task_pool.extend(maintenance)
                
                # 2. Pick a task if the matrix isn't overwhelmed
                # (Simulated check: in production we'd check cell queue sizes)
                selected_task = random.choice(task_pool)
                
                logger.info(f"🆕 BACKLOG: Auto-generating task: {selected_task}")
                
                # 3. Dispatch to Swarm
                async for step in self.orchestrator.submit_task_stream(selected_task, "autonomous_backlog"):
                    if step["status"] == "completed":
                        logger.info(f"✅ BACKLOG TASK COMPLETE: {selected_task[:30]}...")
                
                # 4. Idle Wait (Dynamic based on revenue/needs)
                wait_time = random.randint(300, 900) # 5-15 minutes
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"Backlog Error: {e}")
                await asyncio.sleep(60)

    def stop(self):
        self.is_running = False
