import hashlib
import json
from datetime import datetime
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
            reg_entry = {
                "id": agent_id,
                "role": agent.config.role,
                "status": "active",
                "tools": agent.config.allowed_tool_ids,
                "version": "1.0.0"
            }
            # Integrity hash for the registry entry
            entry_data = json.dumps(reg_entry, sort_keys=True)
            reg_entry["integrity_hash"] = hashlib.sha256(entry_data.encode()).hexdigest()
            
            self.agent_registry.append(reg_entry)
            logger.info(f"Forge registered agent: {agent.config.name} ({agent.config.role}) with hash {reg_entry['integrity_hash'][:8]}")

    def list_agents(self) -> List[Dict[str, Any]]:
        return self.agent_registry

    def health_check_agents(self) -> Dict[str, str]:
        results = {}
        for agent_id, agent in self.agents.items():
            try:
                if agent:
                    # Capture hash of the agent config for audit
                    results[agent_id] = "OK"
                else:
                    results[agent_id] = "FAIL"
            except Exception as e:
                logger.error(f"Agent {agent_id} health check failed: {e}")
                results[agent_id] = f"ERROR: {str(e)}"
        return results

    def route_task(self, task_spec: TaskSpec) -> Dict[str, Any]:
        target_agent_id = "pm"
        desc = task_spec.description.lower()
        
        # 1. Broad Department/Role Mapping
        routing_map = {
            "seo": "seo_strategy_lead",
            "pricing": "saas_pricing_strategist",
            "security": "cybersecurity_analyst",
            "mobile": "mobile_app_developer_ios",
            "legal": "contract_review_agent",
            "audit": "statistical_auditor",
            "design": "ui_visual_designer",
            "blockchain": "blockchain_developer",
            "cloud": "cloud_infrastructure_architect"
        }
        
        for keyword, agent_id in routing_map.items():
            if keyword in desc:
                target_agent_id = agent_id
                break
        
        # 2. Refined Fallback logic (existing)
        if target_agent_id == "pm":
            if any(k in desc for k in ["code", "implement", "logic", "refactor"]):
                target_agent_id = "dev"
            elif any(k in desc for k in ["deploy", "docker", "infra", "compose"]):
                target_agent_id = "devops"
            elif any(k in desc for k in ["test", "verify", "check", "qa"]):
                target_agent_id = "qa"
            elif any(k in desc for k in ["market", "content", "blog", "growth"]):
                target_agent_id = "growth_hacker"
        
        agent = self.agents.get(target_agent_id)
        if not agent:
            logger.error(f"Forge failed to find agent {target_agent_id}")
            return {"status": "failed", "error": f"Target agent {target_agent_id} not found"}
            
        logger.info(f"Forge routing task to {target_agent_id} (ID: {agent.config.id})")
        return agent.process_task(task_spec)
