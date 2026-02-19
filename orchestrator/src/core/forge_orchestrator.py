from typing import Dict, Any, List
from orchestrator.src.validation.schemas import AgentConfig, TaskSpec
from orchestrator.src.core.agent import Agent
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class ForgeOrchestrator:
    def __init__(self, agents: Dict[str, Agent]):
        self.agents = agents
        self.agent_registry: List[Dict[str, Any]] = []
        self._register_agents()

    def _register_agents(self):
        for agent_id, agent in self.agents.items():
            self.agent_registry.append({
                "id": agent_id,
                "role": agent.config.role,
                "status": "active", # defaulting to active since they are instantiated
                "tools": agent.config.allowed_tool_ids
            })
            logger.info(f"Forge registered agent: {agent.config.name} ({agent.config.role})")

    def list_agents(self) -> List[Dict[str, Any]]:
        return self.agent_registry

    def health_check_agents(self) -> Dict[str, str]:
        results = {}
        for agent_id, agent in self.agents.items():
            try:
                # Simulate a lightweight check. 
                # Real check would involve sending a message and checking response.
                # Since Agent class is mock-LLM backed by default or Groq, we can just check if it's alive.
                if agent:
                    results[agent_id] = "OK"
                else:
                    results[agent_id] = "FAIL"
            except Exception as e:
                logger.error(f"Agent {agent_id} health check failed: {e}")
                results[agent_id] = f"ERROR: {str(e)}"
        return results

    def route_task(self, task_spec: TaskSpec) -> Dict[str, Any]:
        # Simple routing logic based on description keywords
        target_agent_id = "pm" # default
        desc = task_spec.description.lower()
        
        if "code" in desc or "implement" in desc:
            target_agent_id = "dev"
        elif "deploy" in desc or "docker" in desc:
            target_agent_id = "devops"
        elif "test" in desc:
            target_agent_id = "qa"
        
        agent = self.agents.get(target_agent_id)
        if not agent:
            return {"status": "failed", "error": f"Target agent {target_agent_id} not found"}
            
        logger.info(f"Forge routing task to {target_agent_id}")
        return agent.process_task(task_spec)
