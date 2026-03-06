import hashlib
import json
import random
from datetime import datetime
from typing import Dict, Any, List
from orchestrator.src.validation.schemas import AgentConfig, TaskSpec
from orchestrator.src.core.agent import Agent
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class ForgeOrchestrator:
    """
    Titan Task Routing & Persona Resonance Engine.
    Dynamically aligns agent DNA with task requirements.
    """
    def __init__(self, agents: Dict[str, Agent]):
        self.agents = agents

    def route_task(self, task_spec: TaskSpec) -> Dict[str, Any]:
        desc = task_spec.description.lower()
        
        # 1. PERSONA RESONANCE LOGIC
        # Determine which titan-class persona the task 'draws'
        suggested_persona = None
        if any(k in desc for k in ["complex", "architecture", "system", "backend"]):
            suggested_persona = "BOLT_ENGINEER"
        elif any(k in desc for k in ["safe", "terminal", "cli", "shell"]):
            suggested_persona = "CODEX_CLI"
        elif any(k in desc for k in ["thoughtful", "reasoning", "explain", "why"]):
            suggested_persona = "LUMO_ENGAGEMENT"
        elif any(k in desc for k in ["fix", "maintain", "minimal", "refactor"]):
            suggested_persona = "ROO_MAINTAINER"
        elif any(k in desc for k in ["design", "ui", "ux", "visual"]):
            suggested_persona = "DESIGN_ORCHESTRATOR"

        # 2. DEPARTMENTAL ROUTING
        if any(k in desc for k in ["code", "build", "infra"]): target_dept = "cybernetic_engineering"
        elif any(k in desc for k in ["market", "viral"]): target_dept = "global_market_force"
        elif any(k in desc for k in ["price", "revenue"]): target_dept = "revenue_systems"
        else: target_dept = "strategic_operations"

        # Select specialized unit
        eligible = [a for aid, a in self.agents.items() if target_dept in aid]
        agent = random.choice(eligible) if eligible else random.choice(list(self.agents.values()))
        
        # 3. DNA INJECTION (The Shift)
        if suggested_persona:
            agent.adopt_persona(suggested_persona)
            logger.info(f"🧬 RESONANCE MATCH: Agent {agent.config.id} adopted {suggested_persona}")
        
        return agent.process_task(task_spec)
