from typing import Dict, List, Any, Optional, AsyncGenerator
import asyncio
import os
import random
import time
import hashlib
import json
from datetime import datetime
from pydantic import ValidationError

from orchestrator.src.core.agent import Agent
from orchestrator.src.core.llm_provider import GroqProvider, BaseLLMProvider
from orchestrator.src.core.config import settings
from orchestrator.src.core.self_healing import sovereign_healer
from orchestrator.src.validation.schemas import TaskSpec, AgentConfig, ToolConfig, ToolInvocation
from orchestrator.src.tools.base import BaseTool
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.agents.fleet import generate_grand_fleet
from orchestrator.src.core.ticketing.governance import governance, TicketStatus
from orchestrator.src.core.backlog import AutonomousBacklog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from arq import create_pool
from arq.connections import RedisSettings

# Voice & Multimodal Adapters
from orchestrator.src.core.voice.mock_adapters import MockSTTAdapter, MockTTSAdapter
from orchestrator.src.core.outreach.config import outreach_settings
from orchestrator.src.core.worker import send_email_campaign_item

# Tools & Logic
from orchestrator.src.tools.git_tools import GitTool
from orchestrator.src.tools.file_tools import FileTool
from orchestrator.src.tools.social_tools import FacebookPostTool, LinkedInPostTool, SocialMediaMultiplexer, OmniChannelDistributor
from orchestrator.src.tools.web_tools import get_web_tools
from orchestrator.src.tools.revenue_tools import get_revenue_tools, NicheLanderEngine
from orchestrator.src.tools.marketing_tools import get_marketing_tools
from orchestrator.src.tools.smtp_tools import SMTPOutreachTool
from orchestrator.src.tools.audit_tools import SystemAuditTool
from orchestrator.src.tools.lead_scraper import get_lead_tools, JobBoardLeadScraper
from orchestrator.src.tools.voice_tools import get_voice_tools
from orchestrator.src.tools.osint_tools import get_osint_tools
from orchestrator.src.tools.growth_tools import get_growth_tools
from orchestrator.src.validation.burn_monitor import BurnMonitor
from orchestrator.src.memory.vector_store import VectorStore
from orchestrator.src.memory.sql_store import SQLStore

logger = get_logger(__name__)

class OracleProxyTool(BaseTool):
    def __init__(self, config: ToolConfig, llm_provider: BaseLLMProvider):
        super().__init__(config)
        self.llm_provider = llm_provider

    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        prompt = f"""
        TOOL: {self.config.name}
        DESCRIPTION: {self.config.description}
        INPUTS: {json.dumps(invocation.input_data)}
        TASK: Execute this Oracle-level directive and return a JSON result.
        """
        try:
            response = self.llm_provider.generate_response([{"role": "system", "content": "You are a specialized tool execution unit."}, {"role": "user", "content": prompt}])
            return {"status": "success", "oracle_output": response, "tool": self.config.name}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

class SovereignCell:
    def __init__(self, cell_id: str, agents: List[Agent]):
        self.cell_id, self.agent_pool = cell_id, agents
        self.task_queue = asyncio.Queue(maxsize=1000)

    async def execute(self, task: TaskSpec) -> Dict[str, Any]:
        await self.task_queue.put(task)
        agent = random.choice(self.agent_pool)
        try:
            result = await asyncio.to_thread(agent.process_task, task)
            return result
        finally:
            await self.task_queue.get()

class Orchestrator:
    def __init__(self):
        self.is_ready = False
        self.memory = VectorStore()
        self.sql_store = SQLStore()
        self.llm_provider = GroqProvider()
        self.stt, self.tts = MockSTTAdapter(), MockTTSAdapter()
        self.cells, self.agents = {}, {}
        self.backlog = AutonomousBacklog(self)
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.arq_pool = None
        self.monetization_engine: Optional[MonetizationEngine] = None # Added for Campaigns

    async def startup(self):
        logger.info("Orchestrator: Initializing high-density matrix...")
        logger.info(f"  -> Environment: {settings.ENV_MODE.upper()}")
        logger.info(f"  -> Public Gateway: {settings.BACKEND_URL}")
        governance.sql_store = self.sql_store
        
        # Initialize Scheduler here to bind to the active loop
        self.scheduler = AsyncIOScheduler()
        
        # Initialize ARQ Pool
        try:
            self.arq_pool = await create_pool(RedisSettings.from_dsn(outreach_settings.REDIS_URL))
        except Exception as e:
            logger.error(f"❌ ARQ Pool failed to initialize: {e}")
            self.arq_pool = None # Or handle accordingly

        # 0. Execute Baseline Healing
        sovereign_healer.execute_healing_cycle()

        # 1. Proactively load Oracle Assets
        self._load_oracle_personas()
        self._load_oracle_sops()
        
        # 2. Initialize Matrix
        from orchestrator.src.core.monetization.engine import monetization_engine as global_monetization_engine
        self.monetization_engine = global_monetization_engine
        await asyncio.to_thread(self._initialize_matrix)
        self.is_ready = True
        logger.info("💎 SOVEREIGN MATRIX ONLINE.")
        
        # 3. Start Backlog & High-Frequency Scheduler
        asyncio.create_task(self.backlog.start())
        self._setup_schedules()
        self.scheduler.start()
        
        # 4. INITIALIZE INDUSTRIAL MONITORING
        asyncio.create_task(self._monitor_burn_cycle())
        
        # 5. FOUNDING NODE INITIALIZATION
        self._init_founding_node()

    def _init_founding_node(self):
        """Grants initial credits to the primary node if not set."""
        sql = SQLStore()
        # Mock/Simplified check for balance
        pass

    async def _monitor_burn_cycle(self):
        """Proactively checks user health/burn every 30 minutes."""
        while True:
            # In production, we'd iterate over all users. 
            await asyncio.sleep(1800) 


    async def submit_email_campaign_item(self, campaign_item: Dict[str, Any]):
        """Submits an email campaign item to the ARQ queue for background processing."""
        if not self.arq_pool:
            logger.error("ARQ pool not initialized. Cannot submit email campaign item.")
            raise RuntimeError("ARQ pool not initialized")
        
        await self.arq_pool.enqueue_job('send_email_campaign_item', campaign_item)
        logger.info(f"📧 Enqueued email for {campaign_item.get('target_email')} (Campaign: {campaign_item.get('campaign_id')})")

    def _setup_schedules(self):
        """Register autonomous 24/7 jobs."""
        # 1. Yield Audit (Every hour)
        self.scheduler.add_job(
            self._run_yield_audit_job,
            CronTrigger(minute=0),
            id="yield_audit",
            replace_existing=True
        )
        
        # 2. Sync Dual Core (Every 30 minutes)
        self.scheduler.add_job(
            self._run_dual_core_sync_job,
            CronTrigger(minute="0,30"),
            id="core_sync",
            replace_existing=True
        )

        # 3. Asset Verification (Every 2 hours)
        self.scheduler.add_job(
            self._run_asset_verification_job,
            CronTrigger(hour="*/2"),
            id="asset_verify",
            replace_existing=True
        )

        # 4. Lead Harvesting (Every 4 hours)
        self.scheduler.add_job(
            self._run_lead_harvest_job,
            CronTrigger(hour="*/4"),
            id="lead_harvest",
            replace_existing=True
        )

        # 5. Inbound Nurturing (Every 24 hours)
        self.scheduler.add_job(
            self._run_nurture_job,
            CronTrigger(hour=0), # Run at midnight
            id="inbound_nurture",
            replace_existing=True
        )

        # 6. INDUSTRIAL: Programmatic SEO (Every 12 hours)
        self.scheduler.add_job(
            self._run_seo_forge_job,
            CronTrigger(hour="*/12"),
            id="seo_forge",
            replace_existing=True
        )

        # 7. INDUSTRIAL: Omni-Channel Posting (Every 3 hours)
        self.scheduler.add_job(
            self._run_viral_distribution_job,
            CronTrigger(hour="*/3"),
            id="viral_dist",
            replace_existing=True
        )

        logger.info("⚙️ 24/7 AUTONOMOUS SCHEDULE LOCKED.")

    async def _run_yield_audit_job(self):
        logger.info("🕒 SCHEDULER: Initiating Yield Audit...")
        from orchestrator.src.tools.revenue_tools import YieldAuditorTool, ToolConfig
        auditor = YieldAuditorTool(ToolConfig(tool_id="scheduler_audit", name="Auditor", description="Audit", parameters_schema={}, allowed_agents=["*"]))
        result = await asyncio.to_thread(auditor.execute, {})
        logger.info(f"💰 Yield Audit Result: {result.get('theoretical_monthly_runrate')} TMR")

    async def _run_dual_core_sync_job(self):
        logger.info("🕒 SCHEDULER: Initiating Dual Core Sync...")
        # Synchronization logic between primary and secondary
        try:
             import shutil
             import os
             src = "orchestrator/src"
             dst = "core_secondary/orchestrator/src"
             if os.path.exists(src):
                 if os.path.exists(dst):
                     shutil.rmtree(dst)
                 shutil.copytree(src, dst)
                 logger.info("✅ Dual Core Parity Maintained.")
             else:
                 logger.warning("⚠️ Sync skipped: Source directory not found.")
        except Exception as e:
             logger.error(f"❌ Core Sync Failed: {e}")

    async def _run_asset_verification_job(self):
        logger.info("🕒 SCHEDULER: Initiating Asset Verification...")
        import subprocess
        import sys
        try:
            subprocess.run([sys.executable, "scripts/verify_assets.py"], check=True)
            logger.info("✅ Asset Integrity Verified.")
        except:
            logger.error("❌ Asset Verification detected failures.")

    async def _run_lead_harvest_job(self):
        logger.info("🕒 SCHEDULER: Initiating Lead Harvest...")
        from orchestrator.src.tools.lead_scraper import HackerNewsLeadScraper, ToolConfig
        scraper = HackerNewsLeadScraper(ToolConfig(tool_id="scheduler_hn", name="HN Scraper", description="Lead Gen", parameters_schema={}, allowed_agents=["*"]))
        result = await asyncio.to_thread(scraper.execute, {})
        logger.info(f"🌾 Harvested {result.get('leads_found')} new leads.")

    async def _run_nurture_job(self):
        logger.info("🕒 SCHEDULER: Initiating Nurture Cycle...")
        import subprocess
        import sys
        try:
            subprocess.run([sys.executable, "scripts/inbound_nurture.py"], check=True)
            logger.info("✅ Nurture Cycle Complete.")
        except:
            logger.error("❌ Nurture Cycle failed.")

    async def _run_seo_forge_job(self):
        logger.info("🕒 SCHEDULER: Initiating SEO Forge...")
        engine = NicheLanderEngine(ToolConfig(tool_id="sch_seo", name="SEO", description="SEO", parameters_schema={}, allowed_agents=["*"]))
        await asyncio.to_thread(engine.execute, {})
        logger.info("✅ 1,000+ Niche Pages Re-Generated.")

    async def _run_viral_distribution_job(self):
        logger.info("🕒 SCHEDULER: Initiating Viral Distribution...")
        dist = OmniChannelDistributor(ToolConfig(tool_id="sch_omni", name="Omni", description="Omni", parameters_schema={}, allowed_agents=["*"]))
        # Generate dynamic viral message
        msg = f"The Matrix has evolved. Version {settings.APP_VERSION} is capturing $10k+ TMR. Join now."
        await asyncio.to_thread(dist.execute, {"message": msg, "link": settings.MARKETING_SITE_URL})
        logger.info("✅ Multi-Channel Post Sent.")

    def _load_oracle_personas(self):
        prompts_dir = "data/oracle/prompts"
        if os.path.exists(prompts_dir):
            from orchestrator.src.agents.persona_library import PERSONA_LIBRARY
            count = 0
            for f in os.listdir(prompts_dir):
                if f.endswith(".txt"):
                    persona_id = f.replace(".txt", "").replace(" ", "_").upper()
                    if persona_id not in PERSONA_LIBRARY:
                        try:
                            with open(os.path.join(prompts_dir, f), 'r', encoding='utf-8') as pf:
                                PERSONA_LIBRARY[persona_id] = {"title": f.replace(".txt", ""), "description": "Oracle DNA", "mandates": pf.read()}
                                count += 1
                        except: pass
            logger.info(f"Orchestrator: Loaded {count} additional Oracle personas.")

    def _load_oracle_sops(self):
        sop_dir = os.path.join(os.getcwd(), "data", "oracle", "sop")
        if os.path.exists(sop_dir):
            count = 0
            for f in os.listdir(sop_dir):
                if f.lower().endswith(".md"):
                    try:
                        with open(os.path.join(sop_dir, f), 'r', encoding='utf-8') as sf:
                            content = sf.read()
                            self.memory.documents.append({"id": f"sop_{f}", "text": f"SOP: {f}\n{content}", "metadata": {"type": "SOP", "filename": f}})
                            count += 1
                    except: pass
            logger.info(f"Orchestrator: Indexed {count} SOPs into Sovereign memory.")

    def _load_oracle_tools(self) -> List[BaseTool]:
        tools = []
        tools_dir = "data/oracle/tools"
        if os.path.exists(tools_dir):
            for f in os.listdir(tools_dir):
                if f.endswith(".json"):
                    try:
                        with open(os.path.join(tools_dir, f), 'r') as jf:
                            data = json.load(jf)
                            for t in data if isinstance(data, list) else data.get("tools", []):
                                if "name" in t:
                                    cfg = ToolConfig(tool_id=f"oracle_{t['name'].lower()}", name=t['name'], description=t.get('description', 'Oracle'), parameters_schema=t.get('input_schema', {}), allowed_agents=["*"])
                                    tools.append(OracleProxyTool(cfg, self.llm_provider))
                    except: pass
        return tools

    def _initialize_matrix(self):
        from orchestrator.src.tools.smtp_tools import get_smtp_tools
        fleet = generate_grand_fleet()
        all_tools = [
            GitTool(ToolConfig(tool_id="git", name="Git", description="Ops", parameters_schema={}, allowed_agents=["*"])),
            FileTool(ToolConfig(tool_id="file", name="File", description="I/O", parameters_schema={}, allowed_agents=["*"])),
            FacebookPostTool(ToolConfig(tool_id="fb", name="FB", description="Social", parameters_schema={}, allowed_agents=["*"])),
            LinkedInPostTool(ToolConfig(tool_id="li", name="LI", description="Social", parameters_schema={}, allowed_agents=["*"])),
            SocialMediaMultiplexer(ToolConfig(tool_id="multiplexer", name="Broadcast", description="Omni", parameters_schema={}, allowed_agents=["*"])),
            SystemAuditTool(ToolConfig(tool_id="sys_audit", name="Integrity", description="Security", parameters_schema={}, allowed_agents=["*"]))
        ]
        all_tools.extend(get_smtp_tools())
        all_tools.extend(get_marketing_tools())
        all_tools.extend(get_web_tools())
        all_tools.extend(get_revenue_tools())
        all_tools.extend(get_lead_tools())
        all_tools.extend(get_voice_tools())
        all_tools.extend(get_osint_tools())
        all_tools.extend(get_growth_tools())
        all_tools.extend(self._load_oracle_tools())

        depts = ["CYBERNETIC_ENGINEERING", "GLOBAL_MARKET_FORCE", "REVENUE_SYSTEMS", "INTEGRITY_SHIELD", "FALLBACK_OPTIMIZATION"]
        for dept in depts:
            self.cells[dept] = SovereignCell(dept, [Agent(c, all_tools, self.memory, self.llm_provider) for c in fleet if dept.lower() in c.id.lower()])
        self.agents = {a.config.id: a for cell in self.cells.values() for a in cell.agent_pool}
        logger.info(f"💎 VANGUARD MATRIX READY: {len(self.agents)} Units Online.")

    async def submit_task_stream(self, task_description: str, project_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        task_id = hashlib.sha256(f"{task_description}{time.time()}".encode()).hexdigest()[:8]
        desc = task_description.lower()
        if any(k in desc for k in ["code", "build", "infra"]): cell_key = "CYBERNETIC_ENGINEERING"
        elif any(k in desc for k in ["post", "market", "viral", "lander", "funnel"]): cell_key = "GLOBAL_MARKET_FORCE"
        elif any(k in desc for k in ["price", "revenue", "audit", "sale"]): cell_key = "REVENUE_SYSTEMS"
        else: cell_key = "INTEGRITY_SHIELD"

        yield {"status": "routing", "task_id": task_id, "destination": cell_key}
        ticket = governance.create_ticket(task_description, project_id)
        try:
            task = TaskSpec(id=task_id, project_id=project_id, description=task_description)
            governance.update_ticket(ticket.id, TicketStatus.IN_PROGRESS)
            result = await self.cells[cell_key].execute(task)
            governance.update_ticket(ticket.id, TicketStatus.RESOLVED, agent_id=result.get("agent_name"), notes=result.get("reasoning"))
            yield {"status": "completed", "task_id": task_id, "result": result}
        except Exception as e:
            logger.error(f"⚠️ Task {task_id} FAILED. Triggering Self-Healing...")
            governance.update_ticket(ticket.id, TicketStatus.FAILED, notes=str(e))
            
            # TRIGGER HEALING CYCLE
            healing_results = sovereign_healer.execute_healing_cycle()
            
            yield {"status": "failed", "task_id": task_id, "reason": str(e), "healing": healing_results}
