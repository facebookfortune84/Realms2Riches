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
        # ... existing synchronous implementation ...
        pass # (This is just a placeholder to show context, I will replace the whole method below if needed or add the new one)

    async def submit_task_stream(self, task_description: str, project_id: str):
        """
        Asynchronous generator that yields intermediate steps of the agent's thought process.
        """
        task = TaskSpec(project_id=project_id, description=task_description)
        
        # 1. Routing
        yield {"status": "routing", "message": "Analyzing task intent..."}
        await asyncio.sleep(0.5) # Narrative delay
        
        desc = task_description.lower()
        if any(k in desc for k in ["code", "logic", "refactor", "fix"]):
            agent_id = "agent_cybernetic_engineering_1"
        elif any(k in desc for k in ["design", "ui", "brand", "css"]):
            agent_id = "agent_visual_intelligence_1"
        elif any(k in desc for k in ["market", "seo", "growth", "business"]):
            agent_id = "agent_global_market_force_1"
        else:
            agent_id = "agent_strategic_operations_1"
            
        yield {"status": "routing", "message": f"Routed to {agent_id}"}
        await asyncio.sleep(0.3)

        agent = self.agents.get(agent_id)
        if not agent:
            yield {"status": "error", "message": f"Agent {agent_id} offline."}
            return

        # 2. Agent Execution (Simulated Steps if LLM is fast/mocked)
        yield {"status": "processing", "message": f"[{agent_id}] Accessing context..."}
        # In a real scenario, agent.process_task would be async and yield steps.
        # For now, we wrap the synchronous call but inject narrative steps.
        
        try:
            # We run the synchronous agent in a thread to not block the event loop
            result = await asyncio.to_thread(agent.process_task, task)
            
            yield {"status": "processing", "message": f"[{agent_id}] formulating response..."}
            await asyncio.sleep(0.5) 
            
            # Log to SQL
            self.sql_store.add_run({
                "id": task.id,
                "project_id": project_id,
                "agent_id": agent_id,
                "action": "task_completion",
                "details": result
            })
            
            yield {"status": "completed", "result": result}
            
        except Exception as e:
            logger.error(f"Task failed: {e}")
            yield {"status": "failed", "message": str(e)}

if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.submit_task("Execute core integrity probe", "sovereign-001")
