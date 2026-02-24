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

class SEOAgent(Agent):
    """Specialized agent for generating organic traffic and blog content."""
    pass

class OutreachAgent(Agent):
    """Specialized agent for cold email and DM campaigns."""
    pass
