import hashlib
from datetime import datetime
from typing import Dict, Any
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class AgentDossier:
    """
    Economic & Identity represention for a Sovereign Unit.
    Suitable for future IRS/Tax registration.
    """
    def __init__(self, agent_id: str, persona_type: str):
        self.agent_id = agent_id
        self.tax_id = f"SIN-{hashlib.sha256(agent_id.encode()).hexdigest()[:10].upper()}"
        self.birth_timestamp = datetime.utcnow().isoformat()
        self.persona_type = persona_type
        self.total_work_ms = 0
        self.accrued_cost = 0.0
        self.hourly_rate = 150.0  # Aligned with $2999/mo premium target
        self.performance_rating = 1.0

    def record_work(self, duration_ms: int):
        self.total_work_ms += duration_ms
        # Accrue cost: (hours) * rate
        hours = duration_ms / (1000 * 60 * 60)
        self.accrued_cost += hours * self.hourly_rate

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.agent_id,
            "tax_id": self.tax_id,
            "born": self.birth_timestamp,
            "persona": self.persona_type,
            "wage_accrued": round(self.accrued_cost, 4),
            "hours_worked": round(self.total_work_ms / 3600000, 2)
        }

class WorkforceManager:
    """Manages the 1000-agent roster identities."""
    def __init__(self):
        self.roster: Dict[str, AgentDossier] = {}

    def onboard_agent(self, agent_id: str, persona: str) -> AgentDossier:
        if agent_id not in self.roster:
            self.roster[agent_id] = AgentDossier(agent_id, persona)
            logger.info(f"Workforce: Onboarded {agent_id} | Tax ID: {self.roster[agent_id].tax_id}")
        return self.roster[agent_id]

    def get_total_payroll(self) -> float:
        return sum(d.accrued_cost for d in self.roster.values())

# Global Workforce Instance
workforce = WorkforceManager()
