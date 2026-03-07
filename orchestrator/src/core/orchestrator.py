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
from orchestrator.src.validation.schemas import TaskSpec, AgentConfig, ToolConfig, ToolInvocation
from orchestrator.src.tools.base import BaseTool
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.agents.fleet import generate_grand_fleet
from orchestrator.src.core.ticketing.governance import governance, TicketStatus
from orchestrator.src.core.backlog import AutonomousBacklog

# Voice & Multimodal Adapters
from orchestrator.src.core.voice.mock_adapters import MockSTTAdapter, MockTTSAdapter

# Tools & Logic
from orchestrator.src.tools.git_tools import GitTool
from orchestrator.src.tools.file_tools import FileTool
from orchestrator.src.tools.social_tools import FacebookPostTool, LinkedInPostTool, SocialMediaMultiplexer
from orchestrator.src.tools.web_tools import get_web_tools
from orchestrator.src.tools.revenue_tools import get_revenue_tools
from orchestrator.src.tools.marketing_tools import get_marketing_tools
from orchestrator.src.tools.smtp_tools import SMTPOutreachTool
from orchestrator.src.tools.audit_tools import SystemAuditTool
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

    async def startup(self):
        logger.info("Orchestrator: Initializing high-density matrix...")
        logger.info(f"  -> Environment: {settings.ENV_MODE.upper()}")
        logger.info(f"  -> Public Gateway: {settings.BACKEND_URL}")
        governance.sql_store = self.sql_store
        
        # 1. Proactively load Oracle Assets
        self._load_oracle_personas()
        self._load_oracle_sops()
        
        # 2. Initialize Matrix
        await asyncio.to_thread(self._initialize_matrix)
        self.is_ready = True
        logger.info("💎 SOVEREIGN MATRIX ONLINE.")
        
        # 3. Start Backlog
        asyncio.create_task(self.backlog.start())

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
        fleet = generate_grand_fleet()
        all_tools = [
            GitTool(ToolConfig(tool_id="git", name="Git", description="Ops", parameters_schema={}, allowed_agents=["*"])),
            FileTool(ToolConfig(tool_id="file", name="File", description="I/O", parameters_schema={}, allowed_agents=["*"])),
            FacebookPostTool(ToolConfig(tool_id="fb", name="FB", description="Social", parameters_schema={}, allowed_agents=["*"])),
            LinkedInPostTool(ToolConfig(tool_id="li", name="LI", description="Social", parameters_schema={}, allowed_agents=["*"])),
            SocialMediaMultiplexer(ToolConfig(tool_id="multiplexer", name="Broadcast", description="Omni", parameters_schema={}, allowed_agents=["*"])),
            SMTPOutreachTool(ToolConfig(tool_id="smtp_outreach", name="SMTP", description="Direct Sales", parameters_schema={}, allowed_agents=["*"])),
            SystemAuditTool(ToolConfig(tool_id="sys_audit", name="Integrity", description="Security", parameters_schema={}, allowed_agents=["*"]))
        ]
        all_tools.extend(get_marketing_tools())
        all_tools.extend(get_web_tools())
        all_tools.extend(get_revenue_tools())
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
            governance.update_ticket(ticket.id, TicketStatus.FAILED, notes=str(e))
            yield {"status": "failed", "task_id": task_id, "reason": str(e)}
