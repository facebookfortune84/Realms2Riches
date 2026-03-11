import asyncio
import os
import sys
import random
import time
from typing import List
import requests

# Ensure orchestrator is in path
sys.path.append(os.getcwd())

from orchestrator.src.logging.logger import get_logger
from orchestrator.src.tools.marketing_tools import get_marketing_tools
from orchestrator.src.tools.smtp_tools import get_smtp_tools
from orchestrator.src.tools.seo_tools import SEOTool, ToolConfig
from orchestrator.src.validation.schemas import ToolInvocation

logger = get_logger("HIGH_VELOCITY_BLITZ")

TRAFFIC_MANAGER_URL = "https://glowfly-sizeable-lazaro.ngrok-free.dev"

# --- CONFIGURATION FOR MAXIMUM REAL SCALE ---
SEO_BATCH_SIZE = 50        # MAX: 50 Real Articles
SOCIAL_BATCH_SIZE = 50     # MAX: 50 Real Scripts
EMAIL_DELAY_SECONDS = 1    # AGGRESSIVE: 1s Delay (Max Legal Speed)

class BlitzCommander:
    def __init__(self):
        self.marketing_tools = {t.config.tool_id: t for t in get_marketing_tools()}
        self.smtp_sender = {t.config.tool_id: t for t in get_smtp_tools()}["smtp_outreach"]
        self.seo_tool = SEOTool(ToolConfig(tool_id="seo_factory", name="SEO", description="SEO", parameters_schema={}, allowed_agents=["*"]))
        
        self.leads = []
        if os.path.exists("data/customers/leads.json"):
            import json
            with open("data/customers/leads.json", "r") as f:
                self.leads = json.load(f)
        
        self.stats = {"seo": 0, "social": 0, "email": 0, "clicks": 0}

    def get_tracking_link(self, target_url: str, source: str, campaign: str) -> str:
        return f"{TRAFFIC_MANAGER_URL}/r?target={target_url}&source={source}&campaign={campaign}"

    def get_real_clicks(self):
        try:
            resp = requests.get(f"{TRAFFIC_MANAGER_URL}/stats", timeout=0.5)
            if resp.status_code == 200:
                data = resp.json()
                return sum(data.values())
        except:
            return 0
        return 0

    async def seo_worker(self, worker_id: int):
        """Worker that relentlessly pumps out SEO content."""
        topics = [
            "AI Agent Revenue", "Sovereign Tech Stack", "Passive Income Automation",
            "Stripe Integration", "Python Orchestration", "Future of Work",
            "Algorithmic Trading", "Digital Sovereignty", "High Frequency Sales",
            "Automated Lead Gen", "SaaS Growth Hacks", "Bootstrap Millions",
            "No-Code Revolution", "API Monetization", "Micro-SaaS Ideas",
            "Remote Empire Building", "Crypto Arbitrage Bots", "Deep Learning Sales",
            "Neural Network Marketing", "Cybernetic Workforce"
        ]
        
        while True:
            if self.stats["seo"] >= SEO_BATCH_SIZE:
                break
                
            topic = f"{random.choice(topics)} {random.randint(1000, 9999)}"
            logger.info(f"📝 [SEO-Worker-{worker_id}] Generating REAL content for: {topic}")
            
            try:
                # Direct execute to bypass overhead
                self.seo_tool.execute({"action": "generate_and_publish", "keywords": [topic, "Automation", "Scale"]})
                self.stats["seo"] += 1
            except Exception as e:
                logger.error(f"SEO Error: {e}")

    async def social_worker(self, worker_id: int):
        """Worker that floods the buffer with viral scripts."""
        products = ["Jarvis 3.5", "Sovereign Kit", "Elite Tier"]
        
        while True:
            if self.stats["social"] >= SOCIAL_BATCH_SIZE:
                break

            prod = random.choice(products)
            logger.info(f"🎥 [Social-Worker-{worker_id}] Ideating viral hook for {prod}")
            
            try:
                invoc = ToolInvocation(tool_id="tiktok_gen", input_data={"product_name": prod}, agent_id=f"social_{worker_id}")
                self.marketing_tools["tiktok_gen"].execute(invoc)
                self.stats["social"] += 1
            except Exception as e:
                logger.error(f"Social Error: {e}")

    async def email_worker(self):
        """The precision striker. Sends emails as fast as legally/technically safe."""
        if not self.leads:
            logger.warning("No leads for Email Worker.")
            return

        logger.info(f"📧 [Email-Command] TARGETING {len(self.leads)} PROSPECTS.")
        
        for lead in self.leads:
            email = lead.get("email") or "robertdemottojr83@gmail.com"
            link = self.get_tracking_link("https://buy.stripe.com/7sY7sLeY1aw1cEWcJJ8so0e", "email", "blitz_v1")
            
            logger.info(f"🔥 [Email-Command] ENGAGING: {email}")
            
            # Generate personalized copy
            invoc_gen = ToolInvocation(
                tool_id="email_gen",
                input_data={"product_name": "Jarvis 3.5", "target_audience": lead.get("name", "Founder")},
                agent_id="blitz_commander"
            )
            res = self.marketing_tools["email_gen"].execute(invoc_gen)
            
            if res.get("status") == "success":
                body = res["email_content"] + f"\n\n🚀 ACCESS GRANTED: {link}"
                
                invoc_smtp = ToolInvocation(
                    tool_id="smtp_outreach",
                    input_data={
                        "target_email": email,
                        "html_body": body,
                        "subject": "URGENT: Sovereign Partnership Opportunity"
                    },
                    agent_id="blitz_commander"
                )
                self.smtp_sender.execute(invoc_smtp)
                self.stats["email"] += 1
                
                await asyncio.sleep(EMAIL_DELAY_SECONDS) 

    async def monitor(self):
        start_time = time.time()
        while True:
            elapsed = time.time() - start_time
            
            # Fetch REAL clicks from the live server
            real_clicks = self.get_real_clicks()
            self.stats["clicks"] = real_clicks

            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"""
            ╔══════════════════════════════════════════════════════════════╗
            ║           🔥 SOVEREIGN HIGH-VELOCITY BLITZ 🔥                ║
            ║                (NO SIMULATION - LIVE FIRE)                   ║
            ╠══════════════════════════════════════════════════════════════╣
            ║  ⏱️  Runtime: {elapsed:.2f}s                                  ║
            ║  📝 SEO Articles Published: {self.stats['seo']} / {SEO_BATCH_SIZE}             ║
            ║  🎥 Viral Scripts Generated: {self.stats['social']} / {SOCIAL_BATCH_SIZE}            ║
            ║  📧 Emails Dispatched: {self.stats['email']} / {len(self.leads)}                  ║
            ║  🖱️  REAL USER CLICKS: {self.stats['clicks']}                             ║
            ╚══════════════════════════════════════════════════════════════╝
            """)
            await asyncio.sleep(1)
            
            # Stop condition
            if (self.stats['seo'] >= SEO_BATCH_SIZE and 
                self.stats['social'] >= SOCIAL_BATCH_SIZE and 
                self.stats['email'] >= len(self.leads)):
                break

    async def launch(self):
        logger.info("🚀 LAUNCHING ALL VECTORS. HOLD ON.")
        
        tasks = []
        
        # Spawn SEO Workers
        for i in range(10): # Increased parallelism
            tasks.append(asyncio.create_task(self.seo_worker(i)))
            
        # Spawn Social Workers
        for i in range(10): # Increased parallelism
            tasks.append(asyncio.create_task(self.social_worker(i)))
            
        # Spawn Email Command (Single thread for safety)
        tasks.append(asyncio.create_task(self.email_worker()))
        
        # Monitor
        await self.monitor()
        
        logger.info("🏆 BLITZ COMPLETE. MAXIMUM PRESSURE APPLIED.")

if __name__ == "__main__":
    commander = BlitzCommander()
    try:
        asyncio.run(commander.launch())
    except KeyboardInterrupt:
        logger.info("Blitz Aborted.")
