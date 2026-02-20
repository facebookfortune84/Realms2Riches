from typing import Dict, List, Any, Optional
import asyncio
import os
from orchestrator.src.core.agent import Agent
from orchestrator.src.core.llm_provider import GroqProvider
from orchestrator.src.validation.schemas import TaskSpec, AgentConfig, ToolConfig
from orchestrator.src.tools.git_tools import GitTool
from orchestrator.src.tools.file_tools import FileTool
from orchestrator.src.memory.vector_store import VectorStore
from orchestrator.src.memory.sql_store import SQLStore
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.agents.fleet import generate_grand_fleet

logger = get_logger(__name__)

class SovereignCell:
    """A specialized sub-swarm handling a specific domain."""
    def __init__(self, cell_id: str, agents: List[Agent]):
        self.cell_id = cell_id
        self.agents = {a.config.id: a for a in agents}
        self.active_tasks = 0

    async def execute(self, task: TaskSpec):
        self.active_tasks += 1
        # Logic to pick the best agent in this cell
        agent = list(self.agents.values())[0] 
        result = await asyncio.to_thread(agent.process_task, task)
        self.active_tasks -= 1
        return result

class Orchestrator:
    def __init__(self):
        self.memory = VectorStore()
        self.sql_store = SQLStore()
        self.llm_provider = GroqProvider()
        self.cells: Dict[str, SovereignCell] = {}
        self._initialize_sovereign_matrix()

    def _initialize_sovereign_matrix(self):
        fleet = generate_grand_fleet()
        
        # Partition 1000 agents into cells
        alpha_agents = [Agent(c, [], self.memory, self.llm_provider) for c in fleet if "Engineering" in c.id or "Cybernetic" in c.id]
        beta_agents = [Agent(c, [], self.memory, self.llm_provider) for c in fleet if "Market" in c.id or "Strategic" in c.id]
        gamma_agents = [Agent(c, [], self.memory, self.llm_provider) for c in fleet if "Legal" in c.id or "Revenue" in c.id]

        self.cells["ALPHA"] = SovereignCell("ALPHA_ENGINEERING", alpha_agents)
        self.cells["BETA"] = SovereignCell("BETA_MARKETING", beta_agents)
        self.cells["GAMMA"] = SovereignCell("GAMMA_STRATEGY", gamma_agents)
        
        # Legacy flat access
        self.agents = {a.config.id: a for a in (alpha_agents + beta_agents + gamma_agents)}
        
        logger.info(f"PLATINUM MATRIX ONLINE: {len(self.cells)} Sovereign Cells Active.")

    async def submit_task_stream(self, task_description: str, project_id: str):
        task = TaskSpec(project_id=project_id, description=task_description)
        
        # Intelligent Cell Routing
        desc = task_description.lower()
        if any(k in desc for k in ["code", "fix", "build"]): target_cell = "ALPHA"
        elif any(k in desc for k in ["market", "post", "social"]): target_cell = "BETA"
        else: target_cell = "GAMMA"

        yield {"status": "routing", "message": f"Diverting to Cell {target_cell}..."}
        
        cell = self.cells[target_cell]
        try:
            result = await cell.execute(task)
            yield {"status": "completed", "result": result}
        except Exception as e:
            yield {"status": "failed", "message": str(e)}

    def get_matrix_status(self):
        return {name: {"active_tasks": c.active_tasks, "agents": len(c.agents)} for name, c in self.cells.items()}
