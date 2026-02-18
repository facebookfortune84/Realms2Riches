from orchestrator.src.core.agent import Agent
from orchestrator.src.validation.schemas import AgentConfig

# This file would typically contain specialized subclasses if agents had 
# drastically different internal logic beyond just prompts and tools.
# For now, the configuration-driven Agent class in core/agent.py suffices.

class ProjectManagerAgent(Agent):
    pass

class DeveloperAgent(Agent):
    pass

class DevOpsAgent(Agent):
    pass
