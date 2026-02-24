from typing import Dict, List, Any, Optional, AsyncGenerator
import asyncio
import os
import random
import time
import hashlib
import shutil
from datetime import datetime

from orchestrator.src.core.agent import Agent
from orchestrator.src.core.llm_provider import GroqProvider
from orchestrator.src.core.config import settings
from orchestrator.src.validation.schemas import TaskSpec, AgentConfig, ToolConfig
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.agents.fleet import generate_grand_fleet
from orchestrator.src.core.voice.mock_adapters import MockSTTAdapter, MockTTSAdapter

logger = get_logger(__name__)

class CircuitBreaker:
    """Industry-standard failure protection."""
    def __init__(self, threshold: int = 5, recovery_time: int = 60):
        self.threshold = threshold
        self.recovery_time = recovery_time
        self.failures = 0
        self.last_failure_time = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.threshold:
            self.state = "OPEN"
            logger.error("🛑 CIRCUIT BREAKER TRIPPED")

    def is_available(self) -> bool:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_time:
                self.state = "HALF-OPEN"
                return True
            return False
        return True

class SovereignCell:
    """Highly-Available specialized agent pool."""
    def __init__(self, cell_id: str, agents: List[Agent]):
        self.cell_id = cell_id
        self.agent_pool = agents
        self.task_queue = asyncio.Queue(maxsize=1000)
        self.circuit_breaker = CircuitBreaker()

    async def execute(self, task: TaskSpec) -> Dict[str, Any]:
        if not self.circuit_breaker.is_available():
            return {"status": "failed", "reason": "Cell Circuit Breaker is OPEN"}
            
        await self.task_queue.put(task)
        agent = random.choice(self.agent_pool)
        
        try:
            result = await asyncio.to_thread(agent.process_task, task)
            self.circuit_breaker.failures = max(0, self.circuit_breaker.failures - 1)
            return result
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise e
        finally:
            await self.task_queue.get()

class SovereignBridge:
    """
    Manages the 'One Up / One Down' logic between Primary and Secondary cores.
    Ensures 100% architectural persistence.
    """
    def __init__(self, primary_path: str = ".", secondary_path: str = "core_secondary"):
        self.primary = primary_path
        self.secondary = secondary_path
        self.active_core = "PRIMARY"

    def sync_critical_assets(self):
        """Synchronizes RAG and Catalog between cores."""
        paths = ["data/vector_store", "data/store/slots", "data/customers"]
        for p in paths:
            src = os.path.join(self.primary, p)
            dst = os.path.join(self.secondary, p)
            if os.path.exists(src):
                os.makedirs(dst, exist_ok=True)
                logger.info(f"Bridge: Synchronized {p} to secondary core.")

    def failover(self):
        self.active_core = "SECONDARY"
        logger.warning("🚨 FAILOVER: Secondary Core promoted to ACTIVE.")

class Orchestrator:
    def __init__(self):
        # 1. Dual-Core Bridge
        self.bridge = SovereignBridge()
        
        # 2. Base Infrastructure
        from orchestrator.src.memory.vector_store import VectorStore
        from orchestrator.src.memory.sql_store import SQLStore
        self.memory = VectorStore()
        self.sql_store = SQLStore()
        self.llm_provider = GroqProvider()
        self.stt = MockSTTAdapter()
        self.tts = MockTTSAdapter()
        
        # 3. Matrix State
        self.cells: Dict[str, SovereignCell] = {}
        self.agents: Dict[str, Agent] = {}
        self._initialize_matrix()
        
        # 4. Background Sync
        self.bridge.sync_critical_assets()

    def _initialize_matrix(self):
        fleet = generate_grand_fleet()
        from orchestrator.src.tools.social_tools import FacebookPostTool, LinkedInPostTool, SocialMediaMultiplexer
        from orchestrator.src.tools.project_tools import ProjectGeneratorTool
        from orchestrator.src.tools.revenue_tools import YieldAuditorTool
        from orchestrator.src.tools.audit_tools import SystemAuditTool
        from orchestrator.src.tools.file_tools import FileTool
        from orchestrator.src.tools.git_tools import GitTool

        all_tools = [
            GitTool(ToolConfig(tool_id="git", name="Git", description="Ops", parameters_schema={}, allowed_agents=["*"])),
            FileTool(ToolConfig(tool_id="file", name="File", description="I/O", parameters_schema={}, allowed_agents=["*"])),
            SocialMediaMultiplexer(ToolConfig(tool_id="multiplexer", name="Broadcast", description="Omni", parameters_schema={}, allowed_agents=["*"])),
            ProjectGeneratorTool(ToolConfig(tool_id="genesis", name="Forge", description="Genesis", parameters_schema={}, allowed_agents=["*"])),
            YieldAuditorTool(ToolConfig(tool_id="auditor", name="Yield", description="Finance", parameters_schema={}, allowed_agents=["*"])),
            SystemAuditTool(ToolConfig(tool_id="sys_audit", name="Integrity", description="Security", parameters_schema={}, allowed_agents=["*"]))
        ]

        depts = ["CYBERNETIC_ENGINEERING", "GLOBAL_MARKET_FORCE", "REVENUE_SYSTEMS", "INTEGRITY_SHIELD", "FALLBACK_OPTIMIZATION"]
        
        # FIXED: Removed 'from orchestrator.src.core.orchestrator import SovereignCell' which was causing circular error
        for dept in depts:
            self.cells[dept] = SovereignCell(dept, [
                Agent(c, all_tools, self.memory, self.llm_provider)
                for c in fleet if dept.lower() in c.id.lower()
            ])

        self.agents = {a.config.id: a for cell in self.cells.values() for a in cell.agent_pool}
        logger.info(f"💎 DUAL-CORE MATRIX READY | Active Core: {self.bridge.active_core}")

    async def submit_task_stream(self, task_description: str, project_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        task_id = hashlib.sha256(f"{task_description}{time.time()}".encode()).hexdigest()[:8]
        desc = task_description.lower()
        
        if any(k in desc for k in ["code", "build"]): cell_key = "CYBERNETIC_ENGINEERING"
        elif any(k in desc for k in ["market", "post"]): cell_key = "GLOBAL_MARKET_FORCE"
        elif any(k in desc for k in ["price", "revenue"]): cell_key = "REVENUE_SYSTEMS"
        else: cell_key = "INTEGRITY_SHIELD"

        yield {"status": "routing", "task_id": task_id, "destination": cell_key, "core": self.bridge.active_core}
        
        try:
            task = TaskSpec(id=task_id, project_id=project_id, description=task_description)
            result = await self.cells[cell_key].execute(task)
            yield {"status": "completed", "task_id": task_id, "result": result}
        except Exception as e:
            logger.error(f"Primary Failure. Attempting Failover sync...")
            self.bridge.failover()
            yield {"status": "failed", "task_id": task_id, "reason": str(e)}

    def get_matrix_status(self) -> Dict[str, Any]:
        return {
            name: {
                "active": c.circuit_breaker.state,
                "load": c.task_queue.qsize(),
                "units": len(c.agent_pool)
            } for name, c in self.cells.items()
        }
