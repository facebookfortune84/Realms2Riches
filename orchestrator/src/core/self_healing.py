import os
import json
import glob
import logging
from typing import List, Dict, Any
from orchestrator.src.core.config import settings

logger = logging.getLogger(__name__)

class SelfHealingService:
    """
    Autonomous logic to repair the Sovereign environment on build/startup.
    Ensures zero-downtime scalability.
    """
    
    REQUIRED_DIRS = [
        "data/assets",
        "data/blog",
        "data/store/slots",
        "data/marketing/images",
        "data/marketing/videos",
        "data/lineage"
    ]

    def __init__(self):
        self.repair_log = []

    def execute_healing_cycle(self):
        logger.info("🛡️ INITIATING SELF-HEALING CYCLE...")
        
        self._repair_directories()
        self._repair_baseline_assets()
        self._validate_product_slots()
        self._verify_environment_integrity()
        self._heal_database_schema()
        
        logger.info(f"✅ HEALING COMPLETE: {len(self.repair_log)} repairs performed.")
        return self.repair_log

    def _heal_database_schema(self):
        """Ensures SQLite/Postgres tables have required columns."""
        import sqlite3
        db_path = "orchestrator.db"
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                # Check for stripe_price_id in prices table
                cursor.execute("PRAGMA table_info(prices)")
                columns = [info[1] for f, info in enumerate(cursor.fetchall())]
                if "stripe_price_id" not in columns:
                    cursor.execute("ALTER TABLE prices ADD COLUMN stripe_price_id TEXT")
                    self.repair_log.append("Healed database: Added stripe_price_id to prices table.")
                conn.commit()
                conn.close()
            except Exception as e:
                logger.warning(f"Database healing skipped (might be Postgres): {e}")

    def _repair_directories(self):
        """Creates any missing critical folders."""
        for d in self.REQUIRED_DIRS:
            if not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
                msg = f"Created missing directory: {d}"
                logger.warning(msg)
                self.repair_log.append(msg)

    def _repair_baseline_assets(self):
        """Restores the Sovereign Strategy Guide if missing."""
        guide_path = "data/assets/sovereign_strategy_guide_v3.txt"
        if not os.path.exists(guide_path):
            with open(guide_path, "w", encoding="utf-8") as f:
                f.write("""🦅 SOVEREIGN STRATEGY GUIDE v3
1. Automate.
2. Scale.
3. Monetize.
""")
            self.repair_log.append("Restored Sovereign Strategy Guide.")

    def _validate_product_slots(self):
        """Scans for corrupt JSON in slots and attempts repair."""
        for f in glob.glob("data/store/slots/*.json"):
            try:
                with open(f, "r") as pf:
                    json.load(pf)
            except Exception as e:
                logger.error(f"Corrupt Slot Detected: {f}. Archiving.")
                target = f + ".corrupt"
                if os.path.exists(target):
                    os.remove(target)
                os.rename(f, target)
                self.repair_log.append(f"Archived corrupt slot: {os.path.basename(f)}")

    def _verify_environment_integrity(self):
        """Checks for placeholder keys in prod and warns if self-healing isn't possible."""
        placeholders = ["placeholder", "gsk-", "Bearer "]
        if settings.STRIPE_API_KEY in placeholders or not settings.STRIPE_API_KEY:
            self.repair_log.append("⚠️ WARNING: Monetization disabled (Missing Stripe Key)")

# Singleton
sovereign_healer = SelfHealingService()
