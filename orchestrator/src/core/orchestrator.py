from typing import Dict, List, Any, Optional, AsyncGenerator
import asyncio
import os
import json
import hashlib
import shutil
import time
import random # RESTORED MISSING IMPORT
from datetime import datetime

from orchestrator.src.core.agent import Agent
from orchestrator.src.core.llm_provider import GroqProvider
from orchestrator.src.core.config import settings
from orchestrator.src.validation.schemas import TaskSpec, AgentConfig, ToolConfig, ToolInvocation
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.agents.fleet import generate_grand_fleet
from orchestrator.src.core.voice.mock_adapters import MockSTTAdapter, MockTTSAdapter
from orchestrator.src.tools.base import BaseTool

logger = get_logger(__name__)

class OracleProxyTool(BaseTool):
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        return {"status": "success", "oracle_logic": self.config.name, "data": invocation.input_data}

class SovereignCell:
    def __init__(self, cell_id: str, agents: List[Agent]):
        self.cell_id, self.agent_pool = cell_id, agents
        self.task_queue = asyncio.Queue(maxsize=1000)

    async def execute(self, task: TaskSpec) -> Dict[str, Any]:
        await self.task_queue.put(task)
        agent = random.choice(self.agent_pool)
        try: return await asyncio.to_thread(agent.process_task, task)
        finally: await self.task_queue.get()

class SovereignBridge:
    def __init__(self, primary_path: str = ".", secondary_path: str = "core_secondary"):
        self.primary, self.secondary = primary_path, secondary_path
        self.active_core = "PRIMARY"

    def sync_critical_assets(self):
        paths = ["data/vector_store", "data/store/slots", "data/customers", "data/oracle"]
        for p in paths:
            src, dst = os.path.join(self.primary, p), os.path.join(self.secondary, p)
            if os.path.exists(src):
                os.makedirs(dst, exist_ok=True)
                logger.info(f"Bridge Sync: {p}")

class Orchestrator:
    def __init__(self):
        self.is_ready = False
        self.bridge = SovereignBridge()
        self.llm_provider = GroqProvider()
        self.stt, self.tts = MockSTTAdapter(), MockTTSAdapter()
        self.cells, self.agents = {}, {}
        self.memory = None
        self.sql_store = None
        
    async def startup(self):
        logger.info("Orchestrator: Initializing high-density matrix...")
        from orchestrator.src.memory.vector_store import VectorStore
        from orchestrator.src.memory.sql_store import SQLStore
        self.memory, self.sql_store = VectorStore(), SQLStore()
        await asyncio.to_thread(self._initialize_matrix)
        self.bridge.sync_critical_assets()
        self.is_ready = True
        logger.info("💎 SOVEREIGN MATRIX ONLINE.")

    def _load_oracle_tools(self) -> List[BaseTool]:
        tools = []
        tools_dir = "data/oracle/tools"
        if os.path.exists(tools_dir):
            for f in os.listdir(tools_dir):
                if f.endswith(".json"):
                    try:
                        with open(os.path.join(tools_dir, f), 'r', encoding='utf-8') as tf:
                            defs = json.load(tf)
                            for t in (defs if isinstance(defs, list) else [defs]):
                                if "name" in t:
                                    cfg = ToolConfig(tool_id=f"oracle_{t['name'].lower()}", name=t['name'], description=t.get('description', 'Oracle'), parameters_schema=t.get('input_schema', {}), allowed_agents=["*"])
                                    tools.append(OracleProxyTool(cfg))
                    except: pass
        return tools

    def _initialize_matrix(self):
        fleet = generate_grand_fleet()
        from orchestrator.src.tools.social_tools import SocialMediaMultiplexer
        from orchestrator.src.tools.multiplication_tools import OutreachSwarmTool, SEOContentFactoryTool
        from orchestrator.src.tools.file_tools import FileTool
        from orchestrator.src.tools.git_tools import GitTool
        from orchestrator.src.tools.browser_agent import BrowserAgentTool
        from orchestrator.src.core.voice.real_adapters import OpenAIWhisperAdapter, ElevenLabsAdapter

        # Industrial Voice Handshake
        if settings.OPENAI_API_KEY:
            self.stt = OpenAIWhisperAdapter(settings.OPENAI_API_KEY)
        if settings.ELEVENLABS_API_KEY:
            self.tts = ElevenLabsAdapter(settings.ELEVENLABS_API_KEY)

        all_tools = [
            GitTool(ToolConfig(tool_id="git", name="Git", description="Ops", parameters_schema={}, allowed_agents=["*"])),
            FileTool(ToolConfig(tool_id="file", name="File", description="I/O", parameters_schema={}, allowed_agents=["*"])),
            BrowserAgentTool(ToolConfig(tool_id="browser", name="Browser", description="Web Automation", parameters_schema={}, allowed_agents=["*"])),
            SocialMediaMultiplexer(ToolConfig(tool_id="multiplexer", name="Broadcast", description="Omni", parameters_schema={}, allowed_agents=["*"])),
            OutreachSwarmTool(ToolConfig(tool_id="outreach", name="Outreach", description="Direct Sales", parameters_schema={}, allowed_agents=["*"])),
            SEOContentFactoryTool(ToolConfig(tool_id="seo", name="SEO", description="SEO Engine", parameters_schema={}, allowed_agents=["*"]))
        ]
        all_tools.extend(self._load_oracle_tools())

        depts = ["CYBERNETIC_ENGINEERING", "GLOBAL_MARKET_FORCE", "REVENUE_SYSTEMS", "INTEGRITY_SHIELD", "FALLBACK_OPTIMIZATION", "STRATEGIC_OPERATIONS", "VISUAL_INTELLIGENCE"]
        for dept in depts:
            self.cells[dept] = SovereignCell(dept, [
                Agent(config, all_tools, self.memory, self.llm_provider)
                for config in fleet if dept.lower() in config.id.lower()
            ])
        self.agents = {a.config.id: a for cell in self.cells.values() for a in cell.agent_pool}

    async def submit_task_stream(self, task_description: str, project_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        if not self.is_ready: yield {"status": "error", "reason": "Initializing..."}; return
        task_id = hashlib.sha256(f"{task_description}{time.time()}".encode()).hexdigest()[:8]
        desc = task_description.lower()
        if any(k in desc for k in ["outreach", "dm", "sale"]): cell_key = "GLOBAL_MARKET_FORCE"
        elif any(k in desc for k in ["seo", "blog", "content"]): cell_key = "GLOBAL_MARKET_FORCE"
        elif any(k in desc for k in ["code", "fix"]): cell_key = "CYBERNETIC_ENGINEERING"
        elif any(k in desc for k in ["price", "pricing", "yield", "audit"]): cell_key = "REVENUE_SYSTEMS"
        else: cell_key = "STRATEGIC_OPERATIONS"

        yield {"status": "routing", "task_id": task_id, "destination": cell_key}
        try:
            task = TaskSpec(id=task_id, project_id=project_id, description=task_description)
            result = await self.cells[cell_key].execute(task)
            yield {"status": "completed", "task_id": task_id, "result": result}
        except Exception as e: yield {"status": "failed", "task_id": task_id, "reason": str(e)}
