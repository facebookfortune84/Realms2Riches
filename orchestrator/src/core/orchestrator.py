from typing import Dict, List, Any, Optional, AsyncGenerator
import asyncio
import os
import random
import time
import hashlib
from datetime import datetime
from pydantic import ValidationError

from orchestrator.src.core.agent import Agent
from orchestrator.src.core.llm_provider import GroqProvider
from orchestrator.src.core.config import settings
from orchestrator.src.validation.schemas import TaskSpec, AgentConfig, ToolConfig, ToolInvocation
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.agents.fleet import generate_grand_fleet

# Voice & Multimodal Adapters
from orchestrator.src.core.voice.mock_adapters import MockSTTAdapter, MockTTSAdapter
# from orchestrator.src.core.voice.real_adapters import DeepgramSTT, ElevenLabsTTS # Ready for expansion

# Tools & Logic
from orchestrator.src.tools.git_tools import GitTool
from orchestrator.src.tools.file_tools import FileTool
from orchestrator.src.tools.social_tools import FacebookPostTool, LinkedInPostTool, SocialMediaMultiplexer
from orchestrator.src.tools.web_tools import WebSearchTool, WebScraperTool
from orchestrator.src.tools.project_tools import ProjectGeneratorTool
from orchestrator.src.tools.revenue_tools import PaymentTool, ProductForgeTool, YieldAuditorTool
from orchestrator.src.tools.audit_tools import SystemAuditTool, SelfHealingOptimizationTool
from orchestrator.src.memory.vector_store import VectorStore
from orchestrator.src.memory.sql_store import SQLStore

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
            logger.error("🛑 CIRCUIT BREAKER TRIPPED: System state set to OPEN.")

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
            self.circuit_breaker.failures = max(0, self.failures_reduction())
            return result
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise e
        finally:
            await self.task_queue.get()

    def failures_reduction(self):
        return self.circuit_breaker.failures - 1

class Orchestrator:
    """
    Sovereign Swarm Master.
    NVIDIA-Style Orchestration with Voice & Telemetry.
    """
    def __init__(self):
        # 1. Base Infrastructure
        self.memory = VectorStore()
        self.sql_store = SQLStore()
        self.llm_provider = GroqProvider()
        
        # 2. Voice Engine (Fixed: Restored for api.py compatibility)
        self.stt = MockSTTAdapter()
        self.tts = MockTTSAdapter()
        
        # 3. Matrix State
        self.cells: Dict[str, SovereignCell] = {}
        self.agents: Dict[str, Agent] = {}
        self._initialize_matrix()

    def _initialize_matrix(self):
        fleet = generate_grand_fleet()
        
        # Load Quad-Core Tools
        all_tools = [
            GitTool(ToolConfig(tool_id="git", name="Git", description="Ops", parameters_schema={}, allowed_agents=["*"])),
            FileTool(ToolConfig(tool_id="file", name="File", description="I/O", parameters_schema={}, allowed_agents=["*"])),
            FacebookPostTool(ToolConfig(tool_id="fb", name="FB", description="Social", parameters_schema={}, allowed_agents=["*"])),
            LinkedInPostTool(ToolConfig(tool_id="li", name="LI", description="Social", parameters_schema={}, allowed_agents=["*"])),
            SocialMediaMultiplexer(ToolConfig(tool_id="multiplexer", name="Broadcast", description="Omni", parameters_schema={}, allowed_agents=["*"])),
            ProjectGeneratorTool(ToolConfig(tool_id="genesis", name="Forge", description="Genesis", parameters_schema={}, allowed_agents=["*"])),
            YieldAuditorTool(ToolConfig(tool_id="auditor", name="Yield", description="Finance", parameters_schema={}, allowed_agents=["*"])),
            SystemAuditTool(ToolConfig(tool_id="sys_audit", name="Integrity", description="Security", parameters_schema={}, allowed_agents=["*"]))
        ]

        # Partition into Meta-Departments
        depts = ["CYBERNETIC_ENGINEERING", "GLOBAL_MARKET_FORCE", "REVENUE_SYSTEMS", "INTEGRITY_SHIELD", "FALLBACK_OPTIMIZATION"]
        for dept in depts:
            self.cells[dept] = SovereignCell(dept, [
                Agent(c, all_tools, self.memory, self.llm_provider)
                for c in fleet if dept.lower() in c.id.lower()
            ])

        self.agents = {a.config.id: a for cell in self.cells.values() for a in cell.agent_pool}
        logger.info(f"💎 PLATINUM BASELINE ESTABLISHED: {len(self.agents)} Specialized Units Online.")

    async def submit_task_stream(self, task_description: str, project_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        task_id = hashlib.sha256(f"{task_description}{time.time()}".encode()).hexdigest()[:8]
        
        desc = task_description.lower()
        if any(k in desc for k in ["code", "build", "infra"]): cell_key = "CYBERNETIC_ENGINEERING"
        elif any(k in desc for k in ["post", "market", "viral"]): cell_key = "GLOBAL_MARKET_FORCE"
        elif any(k in desc for k in ["price", "revenue", "audit"]): cell_key = "REVENUE_SYSTEMS"
        else: cell_key = "INTEGRITY_SHIELD"

        yield {"status": "routing", "task_id": task_id, "destination": cell_key}
        
        try:
            task = TaskSpec(id=task_id, project_id=project_id, description=task_description)
            result = await self.cells[cell_key].execute(task)
            yield {"status": "completed", "task_id": task_id, "result": result}
        except Exception as e:
            logger.error(f"Execution Deviation in {cell_key}: {e}")
            yield {"status": "failed", "task_id": task_id, "reason": str(e)}

    def get_matrix_status(self) -> Dict[str, Any]:
        return {
            name: {
                "active": c.circuit_breaker.state,
                "load": c.task_queue.qsize(),
                "units": len(c.agent_pool)
            } for name, c in self.cells.items()
        }
