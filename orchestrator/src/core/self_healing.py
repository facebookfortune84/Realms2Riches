import os
import json
import glob
import logging
import sqlite3
from typing import List, Dict, Any
from orchestrator.src.core.config import settings

logger = logging.getLogger(__name__)

class SelfHealingService:
    """
    Vanguard Self-Healing Service.
    Autonomously maintains system integrity and directory alignment.
    """
    REQUIRED_DIRS = [
        "data/logs", "data/vector_store", "data/customers", 
        "data/oracle/sop", "data/oracle/tools", "projects/generated/landers"
    ]

    def __init__(self):
        self.repair_log = []
        self._initialize_environment()

    def _initialize_environment(self):
        for d in self.REQUIRED_DIRS:
            if not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
                self.repair_log.append(f"🛠️ REPAIR: Created missing directory {d}")
        
        self._verify_environment_integrity()

    def _verify_environment_integrity(self):
        if not settings.STRIPE_API_KEY:
            self.repair_log.append("⚠️ MONETIZATION: Stripe Key is MISSING.")
        if not settings.GROQ_API_KEY:
            self.repair_log.append("⚠️ INTELLIGENCE: Groq Key is MISSING.")

    def get_maintenance_tasks(self) -> List[str]:
        """Provides upkeep tasks for the autonomous backlog."""
        tasks = []
        # Directory Drift Check
        for d in self.REQUIRED_DIRS:
            if not os.path.exists(d):
                tasks.append(f"Repair missing directory: {d}")
        
        # Log Pruning Check
        log_file = "data/logs/swarm_activity.log"
        if os.path.exists(log_file) and os.path.getsize(log_file) > 10 * 1024 * 1024:
            tasks.append("Prune and rotate large system logs.")
            
        # Standard Industrial Maintenance
        tasks.append("Audit SQLStore for orphaned task records.")
        tasks.append("Sync Oracle assets with Sovereign Secondary Core.")
        
        return tasks

# Singleton
sovereign_healer = SelfHealingService()
