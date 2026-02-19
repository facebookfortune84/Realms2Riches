from typing import Dict, List
import os
from orchestrator.src.core.agent import Agent
from orchestrator.src.core.llm_provider import GroqProvider
from orchestrator.src.validation.schemas import TaskSpec, AgentConfig, ToolConfig
from orchestrator.src.tools.git_tools import GitTool
from orchestrator.src.tools.file_tools import FileTool
from orchestrator.src.tools.docker_tools import DockerTool
from orchestrator.src.memory.vector_store import VectorStore
from orchestrator.src.memory.sql_store import SQLStore
from orchestrator.src.logging.logger import get_logger

from orchestrator.src.agents.fleet import generate_fleet_configs
from orchestrator.src.tools.universal_tools import get_universal_tools

logger = get_logger(__name__)

class Orchestrator:
    def __init__(self):
        self.memory = VectorStore()
        self.sql_store = SQLStore()
        # Initialize Provider
        self.llm_provider = GroqProvider()
        self.agents: Dict[str, Agent] = {}
        self._initialize_agents()

    def _initialize_agents(self):
        # 1. Define standard & universal tools
        git_tool = GitTool(ToolConfig(
            tool_id="git_tool", name="Git", description="Git operations", 
            parameters_schema={}, allowed_agents=["*"]
        ))
        file_tool = FileTool(ToolConfig(
            tool_id="file_tool", name="File", description="File operations", 
            parameters_schema={}, allowed_agents=["*"]
        ))
        docker_tool = DockerTool(ToolConfig(
            tool_id="docker_tool", name="Docker", description="Docker operations", 
            parameters_schema={}, allowed_agents=["devops"]
        ))
        
        all_tools = [git_tool, file_tool, docker_tool] + get_universal_tools()

        # 2. Instantiate Core Agents
        pm_config = AgentConfig(name="Project Manager", role="PM", description="Oversees project", system_prompt="You are a PM.", allowed_tool_ids=["git_tool", "file_tool"])
        dev_config = AgentConfig(name="Developer", role="Dev", description="Writes code", system_prompt="You are a Dev.", allowed_tool_ids=["git_tool", "file_tool"])
        devops_config = AgentConfig(name="DevOps", role="DevOps", description="Deployments", system_prompt="You are DevOps.", allowed_tool_ids=["git_tool", "file_tool", "docker_tool"])

        self.agents["pm"] = Agent(pm_config, all_tools, self.memory, self.llm_provider)
        self.agents["dev"] = Agent(dev_config, all_tools, self.memory, self.llm_provider)
        self.agents["devops"] = Agent(devops_config, all_tools, self.memory, self.llm_provider)

        # 3. Instantiate Global Fleet (100+ Specialized Agents)
        fleet_configs = generate_fleet_configs()
        for config in fleet_configs:
            self.agents[config.id] = Agent(config, all_tools, self.memory, self.llm_provider)

        logger.info(f"Orchestrator initialized with {len(self.agents)} agents and expanded toolset")

    def submit_task(self, task_description: str, project_id: str):
        # Create Task
        task = TaskSpec(project_id=project_id, description=task_description)
        
        # Assign Agent (Routing Logic)
        agent_id = "pm" # Default entry point
        if "deploy" in task_description.lower():
            agent_id = "devops"
        elif "code" in task_description.lower():
            agent_id = "dev"
            
        logger.info(f"Routing task to {agent_id}")
        
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
    # Simple CLI entry point for testing
    orchestrator = Orchestrator()
    orchestrator.submit_task("Check git status", "proj-001")
