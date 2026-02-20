from typing import Dict, List, Any, Optional
import asyncio
import os
import random
from orchestrator.src.core.agent import Agent
from orchestrator.src.core.llm_provider import GroqProvider
from orchestrator.src.validation.schemas import TaskSpec, AgentConfig, ToolConfig
from orchestrator.src.tools.git_tools import GitTool
from orchestrator.src.tools.file_tools import FileTool
from orchestrator.src.tools.universal_tools import get_multiplexer_tool
from orchestrator.src.memory.vector_store import VectorStore
from orchestrator.src.memory.sql_store import SQLStore
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.agents.fleet import generate_grand_fleet

logger = get_logger(__name__)

class SovereignCell:
    """A specialized sub-swarm handling a specific domain."""
    def __init__(self, cell_id: str, agents: List[Agent]):
        self.cell_id = cell_id
        self.agent_pool = agents
        self.agents = {a.config.id: a for a in agents}
        self.active_tasks = 0

    async def execute(self, task: TaskSpec):
        self.active_tasks += 1
        # Platinum Routing: Random selection from specialized pool for hyper-parallelism
        agent = random.choice(self.agent_pool)
        try:
            result = await asyncio.to_thread(agent.process_task, task)
            return result
        finally:
            self.active_tasks -= 1

class Orchestrator:
    def __init__(self):
        self.memory = VectorStore()
        self.sql_store = SQLStore()
        self.llm_provider = GroqProvider()
        self.cells: Dict[str, SovereignCell] = {}
        self._initialize_sovereign_matrix()

    def _initialize_sovereign_matrix(self):
        # 1. Initialize Tools
        git_tool = GitTool(ToolConfig(tool_id="git", name="Git", description="Git ops", parameters_schema={}, allowed_agents=["*"]))
        file_tool = FileTool(ToolConfig(tool_id="file", name="File", description="File ops", parameters_schema={}, allowed_agents=["*"]))
        multiplexer = get_multiplexer_tool()
        all_tools = [git_tool, file_tool, multiplexer]

        # 2. Get Fleet Configs
        fleet = generate_grand_fleet()
        
        # 3. Instantiate Agents with Tools
        alpha_agents = [Agent(c, all_tools, self.memory, self.llm_provider) for c in fleet if any(k in c.id for k in ["Engineering", "Cybernetic"])]
        beta_agents = [Agent(c, all_tools, self.memory, self.llm_provider) for c in fleet if any(k in c.id for k in ["Market", "Strategic"])]
        gamma_agents = [Agent(c, all_tools, self.memory, self.llm_provider) for c in fleet if any(k in c.id for k in ["Legal", "Revenue"])]

        # 4. Map to Cells
        self.cells["ALPHA"] = SovereignCell("ALPHA_ENGINEERING", alpha_agents)
        self.cells["BETA"] = SovereignCell("BETA_MARKETING", beta_agents)
        self.cells["GAMMA"] = SovereignCell("GAMMA_STRATEGY", gamma_agents)
        
        # Legacy flat access for specific routing
        self.agents = {a.config.id: a for a in (alpha_agents + beta_agents + gamma_agents)}
        
        logger.info(f"PLATINUM MATRIX ONLINE: {len(self.cells)} Sovereign Cells Active with 1000 Agents.")

    async def submit_task_stream(self, task_description: str, project_id: str):
        task = TaskSpec(project_id=project_id, description=task_description)
        
        # Intelligent Cell Routing
        desc = task_description.lower()
        if any(k in desc for k in ["code", "fix", "build", "logic", "docker"]): target_cell = "ALPHA"
        elif any(k in desc for k in ["market", "post", "social", "outreach", "seo"]): target_cell = "BETA"
        else: target_cell = "GAMMA"

        yield {"status": "routing", "message": f"Diverting directive to Cell {target_cell}..."}
        
        cell = self.cells.get(target_cell, self.cells["GAMMA"])
        try:
            result = await cell.execute(task)
            yield {"status": "completed", "result": result}
        except Exception as e:
            logger.error(f"Cell Execution Failed: {e}")
            yield {"status": "failed", "message": str(e)}

    def get_matrix_status(self):
        return {name: {"active_tasks": c.active_tasks, "agents": len(c.agents)} for name, c in self.cells.items()}
