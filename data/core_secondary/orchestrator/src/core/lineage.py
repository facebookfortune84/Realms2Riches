import os
import json
import hashlib
from datetime import datetime
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class LineageRegistry:
    """
    Cryptographic Lineage Tracker.
    Records agent contributions with SHA-256 fingerprints.
    """
    def __init__(self, lineage_dir: str = "data/lineage"):
        self.lineage_dir = lineage_dir
        os.makedirs(self.lineage_dir, exist_ok=True)

    def record_contribution(self, agent_id: str, tax_id: str, action: str, artifacts: list, cost: float):
        """Records a bit-level entry for an agent's work."""
        timestamp = datetime.utcnow().isoformat()
        
        # 1. Generate unique entry ID
        payload = f"{agent_id}{timestamp}{action}{json.dumps(artifacts)}"
        fingerprint = hashlib.sha256(payload.encode()).hexdigest()
        
        entry = {
            "fingerprint": fingerprint,
            "agent_id": agent_id,
            "tax_id": tax_id,
            "timestamp": timestamp,
            "action": action,
            "artifacts": artifacts,
            "accrued_wage": cost,
            "status": "VERIFIED"
        }
        
        # 2. Persist to lineage store
        filename = f"contribution_{fingerprint[:12]}.json"
        filepath = os.path.join(self.lineage_dir, filename)
        
        with open(filepath, "w") as f:
            json.dump(entry, f, indent=2)
            
        logger.info(f"Lineage: Artifact {fingerprint[:8]} signed by {agent_id}.")
        return fingerprint

# Global Lineage Instance
lineage_registry = LineageRegistry()
