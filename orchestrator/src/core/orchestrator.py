from typing import Dict, List, Any, Optional, AsyncGenerator
import asyncio
import os
import json
import hashlib
import shutil
import time
from datetime import datetime

from orchestrator.src.core.agent import Agent
from orchestrator.src.core.llm_provider import GroqProvider
from orchestrator.src.core.config import settings
from orchestrator.src.validation.schemas import TaskSpec, AgentConfig, ToolConfig
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.agents.fleet import generate_grand_fleet
from orchestrator.src.core.voice.mock_adapters import MockSTTAdapter, MockTTSAdapter
from orchestrator.src.tools.base import BaseTool

logger = get_logger(__name__)

class SovereignCell:
    def __init__(self, cell_id: str, agents: List[Agent]):
        self.cell_id = cell_id
        self.agent_pool = agents
        self.task_queue = asyncio.Queue(maxsize=1000)
        self.circuit_breaker_failures = 0

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
        self.memory = None
        self.sql_store = None
        self.llm_provider = GroqProvider()
        self.stt, self.tts = MockSTTAdapter(), MockTTSAdapter()
        self.cells, self.agents = {}, {}
        
    async def startup(self):
        """Asynchronous boot sequence to prevent loop blocking."""
        logger.info("Orchestrator: Initializing high-density matrix...")
        
        # 1. Base Infrastructure
        from orchestrator.src.memory.vector_store import VectorStore
        from orchestrator.src.memory.sql_store import SQLStore
        self.memory = VectorStore()
        self.sql_store = SQLStore()
        
        # 2. Build Matrix in Thread to keep API alive
        await asyncio.to_thread(self._initialize_matrix)
        
        self.is_ready = True
        logger.info("💎 SOVEREIGN MATRIX ONLINE.")

    def _initialize_matrix(self):
        fleet = generate_grand_fleet()
        from orchestrator.src.tools.social_tools import SocialMediaMultiplexer
        from orchestrator.src.tools.project_tools import ProjectGeneratorTool
        from orchestrator.src.tools.revenue_tools import YieldAuditorTool
        from orchestrator.src.tools.audit_tools import SystemAuditTool
        from orchestrator.src.tools.file_tools import FileTool
        from orchestrator.src.tools.git_tools import GitTool
        from orchestrator.src.tools.browser_agent import BrowserAgentTool

        all_tools = [
            GitTool(ToolConfig(tool_id="git", name="Git", description="Ops", parameters_schema={}, allowed_agents=["*"])),
            FileTool(ToolConfig(tool_id="file", name="File", description="I/O", parameters_schema={}, allowed_agents=["*"])),
            BrowserAgentTool(ToolConfig(tool_id="browser", name="Browser", description="Web Automation", parameters_schema={}, allowed_agents=["*"])),
            SocialMediaMultiplexer(ToolConfig(tool_id="multiplexer", name="Broadcast", description="Omni", parameters_schema={}, allowed_agents=["*"])),
            ProjectGeneratorTool(ToolConfig(tool_id="genesis", name="Forge", description="Genesis", parameters_schema={}, allowed_agents=["*"])),
            YieldAuditorTool(ToolConfig(tool_id="auditor", name="Yield", description="Finance", parameters_schema={}, allowed_agents=["*"])),
            SystemAuditTool(ToolConfig(tool_id="sys_audit", name="Integrity", description="Security", parameters_schema={}, allowed_agents=["*"]))
        ]

        depts = ["CYBERNETIC_ENGINEERING", "GLOBAL_MARKET_FORCE", "REVENUE_SYSTEMS", "INTEGRITY_SHIELD", "FALLBACK_OPTIMIZATION", "STRATEGIC_OPERATIONS", "VISUAL_INTELLIGENCE"]
        for dept in depts:
            self.cells[dept] = SovereignCell(dept, [
                Agent(c, all_tools, self.memory, self.llm_provider)
                for c in fleet if dept.lower() in c.id.lower()
            ])

        self.agents = {a.config.id: a for cell in self.cells.values() for a in cell.agent_pool}

    async def submit_task_stream(self, task_description: str, project_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        if not self.is_ready:
            yield {"status": "error", "reason": "Orchestrator not yet initialized."}
            return

        task_id = hashlib.sha256(f"{task_description}{time.time()}".encode()).hexdigest()[:8]
        desc = task_description.lower()
        if any(k in desc for k in ["code", "build"]): cell_key = "CYBERNETIC_ENGINEERING"
        elif any(k in desc for k in ["market", "post"]): cell_key = "GLOBAL_MARKET_FORCE"
        elif any(k in desc for k in ["price", "revenue"]): cell_key = "REVENUE_SYSTEMS"
        else: cell_key = "INTEGRITY_SHIELD"

        yield {"status": "routing", "task_id": task_id, "destination": cell_key}
        try:
            task = TaskSpec(id=task_id, project_id=project_id, description=task_description)
            result = await self.cells[cell_key].execute(task)
            yield {"status": "completed", "task_id": task_id, "result": result}
        except Exception as e:
            yield {"status": "failed", "task_id": task_id, "reason": str(e)}
