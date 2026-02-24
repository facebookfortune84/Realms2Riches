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
    Advanced Task Routing Engine.
    Aligns user directives with the 1000-agent Grand Fleet meta-departments.
    """
    def __init__(self, agents: Dict[str, Agent]):
        self.agents = agents
        self.agent_registry: List[Dict[str, Any]] = []
        self._register_agents()

    def _register_agents(self):
        for agent_id, agent in self.agents.items():
            reg_entry = {
                "id": agent_id,
                "role": agent.config.role,
                "status": "active",
                "tools": list(agent.tools.keys()),
                "version": "1.0.0"
            }
            # Integrity hash for the registry entry
            entry_data = json.dumps(reg_entry, sort_keys=True)
            reg_entry["integrity_hash"] = hashlib.sha256(entry_data.encode()).hexdigest()
            
            self.agent_registry.append(reg_entry)

    def list_agents(self) -> List[Dict[str, Any]]:
        return self.agent_registry

    def route_task(self, task_spec: TaskSpec) -> Dict[str, Any]:
        """
        Dynamically routes tasks based on Meta-Department specializations.
        """
        desc = task_spec.description.lower()
        
        # 1. Logic Engineering / DevOps -> CYBERNETIC ENGINEERING
        if any(k in desc for k in ["code", "script", "database", "fix", "logic", "optimize", "kernel", "build", "scaffold"]):
            target_meta = "cybernetic_engineering"
        
        # 2. SEO / Viral / Marketing -> GLOBAL MARKET FORCE
        elif any(k in desc for k in ["market", "seo", "viral", "post", "social", "growth", "content", "copy"]):
            target_meta = "global_market_force"
            
        # 3. Revenue / Pricing / Fintech -> REVENUE SYSTEMS
        elif any(k in desc for k in ["price", "revenue", "fiscal", "stripe", "monetize", "audit", "yield"]):
            target_meta = "revenue_systems"
            
        # 4. Design / 3D / Brand -> VISUAL INTELLIGENCE
        elif any(k in desc for k in ["design", "image", "video", "render", "ui", "ux", "brand", "logo"]):
            target_meta = "visual_intelligence"
            
        # 5. Security / Ethics / Compliance -> INTEGRITY SHIELD
        elif any(k in desc for k in ["security", "ethics", "compliance", "gdpr", "shield", "protect", "integrity"]):
            target_meta = "integrity_shield"
            
        # 6. Fallback / Self-Healing / Audit -> FALLBACK OPTIMIZATION
        elif any(k in desc for k in ["heal", "repair", "audit", "optimize", "fix", "recover"]):
            target_meta = "fallback_optimization"
            
        # 7. Default -> STRATEGIC OPERATIONS
        else:
            target_meta = "strategic_operations"

        # Find agents in the target meta department
        eligible_agents = [a for aid, a in self.agents.items() if target_meta in aid]
        
        if not eligible_agents:
            logger.warning(f"No agents found for meta-dept {target_meta}. Falling back to random selection.")
            target_agent = random.choice(list(self.agents.values()))
        else:
            # Pick a specialized unit from the department
            target_agent = random.choice(eligible_agents)
            
        logger.info(f"Forge routing task to {target_agent.config.id} in department {target_meta}")
        return target_agent.process_task(task_spec)
