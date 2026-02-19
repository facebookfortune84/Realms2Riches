from typing import Dict, List, Any
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
from orchestrator.src.tools.universal_tools import get_multiplexer_tool

logger = get_logger(__name__)

class Orchestrator:
    def __init__(self):
        self.memory = VectorStore()
        self.sql_store = SQLStore()
        self.llm_provider = GroqProvider()
        self.agents: Dict[str, Agent] = {}
        self._initialize_agents()

    def _initialize_agents(self):
        # 1. Initialize High-Scale Multiplexer
        multiplexer = get_multiplexer_tool()
        
        # 2. Base Toolset
        git_tool = GitTool(ToolConfig(tool_id="git_tool", name="Git", description="Git ops", parameters_schema={}, allowed_agents=["*"]))
        file_tool = FileTool(ToolConfig(tool_id="file_tool", name="File", description="File ops", parameters_schema={}, allowed_agents=["*"]))
        all_tools = [git_tool, file_tool, multiplexer]

        # 3. Instantiate Grand Fleet (1000 Specialized Units)
        fleet_configs = generate_grand_fleet()
        for config in fleet_configs:
            self.agents[config.id] = Agent(config, all_tools, self.memory, self.llm_provider)

        logger.info(f"Sovereign Orchestrator initialized with {len(self.agents)} agents and 150+ multiplexed capabilities.")

    def submit_task(self, task_description: str, project_id: str):
        task = TaskSpec(project_id=project_id, description=task_description)
        
        # High-Scale Routing Logic
        agent_id = "agent_strategic_operations_1" # Default to Strategic Ops
        
        desc = task_description.lower()
        if any(k in desc for k in ["code", "logic", "refactor"]):
            agent_id = "agent_cybernetic_engineering_1"
        elif any(k in desc for k in ["design", "ui", "brand"]):
            agent_id = "agent_visual_intelligence_1"
        elif any(k in desc for k in ["market", "seo", "growth"]):
            agent_id = "agent_global_market_force_1"
            
        logger.info(f"Forge routing task to {agent_id}")
        
        agent = self.agents.get(agent_id)
        if agent:
            result = agent.process_task(task)
            self.sql_store.add_run({
                "id": task.id,
                "project_id": project_id,
                "agent_id": agent_id,
                "action": "task_completion",
                "details": result
            })
            return result
        else:
            logger.error(f"Agent {agent_id} not found")
            return {"status": "failed", "reason": "Agent not found"}

if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.submit_task("Execute core integrity probe", "sovereign-001")
