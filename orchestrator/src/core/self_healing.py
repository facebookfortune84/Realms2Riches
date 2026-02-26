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
    Platinum Self-Healing Service.
    Autonomously repairs the Sovereign environment on build/startup.
    Guarantees architectural alignment and data integrity.
    """
    
    REQUIRED_DIRS = [
        "data/assets",
        "data/blog",
        "data/store/slots",
        "data/marketing/images",
        "data/marketing/videos",
        "data/lineage",
        "data/customers",
        "data/vector_store"
    ]

    def __init__(self):
        self.repair_log = []

    def execute_healing_cycle(self):
        logger.info("🛡️ INITIATING GLOBAL HEALING CYCLE...")
        
        self._repair_directories()
        self._repair_baseline_assets()
        self._validate_product_slots()
        self._heal_database_schema()
        self._verify_rag_integrity()
        self._verify_environment_integrity()
        
        logger.info(f"✅ HEALING COMPLETE: {len(self.repair_log)} repairs performed.")
        return self.repair_log

    def route_to_secondary_core(self, file_path: str, error_msg: str):
        """Pass failed code/logic to the 2nd core for background repair and testing."""
        import shutil
        target_dir = "core_secondary/quarantine"
        os.makedirs(target_dir, exist_ok=True)
        base_name = os.path.basename(file_path)
        quarantine_path = os.path.join(target_dir, base_name)
        
        try:
            shutil.copy2(file_path, quarantine_path)
            # Create a repair ticket for the secondary core
            repair_ticket = f"{quarantine_path}.ticket.json"
            with open(repair_ticket, "w") as f:
                json.dump({"error": error_msg, "original_path": file_path, "status": "PENDING_REPAIR"}, f)
            logger.warning(f"🚨 [SELF-HEALING] Routed {base_name} to 2nd Core Quarantine due to: {error_msg}")
            self.repair_log.append(f"Routed {base_name} to secondary core.")
            return True
        except Exception as e:
            logger.error(f"Failed to route {file_path} to secondary core: {e}")
            return False

    def _repair_directories(self):
        for d in self.REQUIRED_DIRS:
            if not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
                msg = f"Restored missing directory: {d}"
                logger.warning(msg)
                self.repair_log.append(msg)

    def _repair_baseline_assets(self):
        guide_path = "data/assets/sovereign_strategy_guide_v3.txt"
        if not os.path.exists(guide_path):
            with open(guide_path, "w", encoding="utf-8") as f:
                f.write("""🦅 SOVEREIGN STRATEGY GUIDE v3
1. Automate EVERYTHING.
2. Scale agents horizontally.
3. Establish direct monetization paths.
4. Maintain cryptographic integrity.
""")
            self.repair_log.append("Restored Sovereign Strategy Guide asset.")

    def _validate_product_slots(self):
        for f in glob.glob("data/store/slots/*.json"):
            try:
                with open(f, "r") as pf:
                    data = json.load(pf)
                    # Purge corrupt/null slots
                    if isinstance(data, dict):
                        if not data.get("id") or data.get("price") is None:
                            os.remove(f)
                            self.repair_log.append(f"Purged malformed slot: {os.path.basename(f)}")
            except Exception as e:
                target = f + ".corrupt"
                if os.path.exists(target): os.remove(target)
                os.rename(f, target)
                self.repair_log.append(f"Quarantined corrupt slot: {os.path.basename(f)}")

    def _heal_database_schema(self):
        from sqlalchemy import create_engine, text
        db_url = settings.db_config.connection_url
        if not db_url: return

        try:
            engine = create_engine(db_url)
            with engine.connect() as conn:
                # 1. Patch Prices table
                res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='prices' AND column_name='stripe_price_id'"))
                if not res.fetchone():
                    conn.execute(text("ALTER TABLE prices ADD COLUMN stripe_price_id TEXT"))
                    self.repair_log.append("Patched Postgres: Added stripe_price_id to 'prices'.")
                
                # 2. Patch Products table
                res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='products' AND column_name='image_url'"))
                if not res.fetchone():
                    conn.execute(text("ALTER TABLE products ADD COLUMN image_url TEXT"))
                    self.repair_log.append("Patched Postgres: Added image_url to 'products'.")

                res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='products' AND column_name='checkout_url'"))
                if not res.fetchone():
                    conn.execute(text("ALTER TABLE products ADD COLUMN checkout_url TEXT"))
                    self.repair_log.append("Patched Postgres: Added checkout_url to 'products'.")
                
                conn.commit()
            engine.dispose()
        except Exception as e:
            logger.warning(f"DB healing (Postgres) skipped or failed: {e}")
            
            # Fallback to SQLite check if local
            db_path = "orchestrator.db"
            if os.path.exists(db_path):
                try:
                    import sqlite3
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    # Patch Prices
                    cursor.execute("PRAGMA table_info(prices)")
                    cols = [info[1] for info in cursor.fetchall()]
                    if "stripe_price_id" not in cols:
                        cursor.execute("ALTER TABLE prices ADD COLUMN stripe_price_id TEXT")
                    # Patch Products
                    cursor.execute("PRAGMA table_info(products)")
                    cols = [info[1] for info in cursor.fetchall()]
                    if "image_url" not in cols:
                        cursor.execute("ALTER TABLE products ADD COLUMN image_url TEXT")
                    if "checkout_url" not in cols:
                        cursor.execute("ALTER TABLE products ADD COLUMN checkout_url TEXT")
                    conn.commit()
                    conn.close()
                except Exception as e2:
                    logger.warning(f"DB healing (SQLite) failed: {e2}")

    def _verify_rag_integrity(self):
        rag_file = "data/vector_store/sovereign_memory.json"
        if os.path.exists(rag_file):
            try:
                with open(rag_file, "r") as f:
                    json.load(f)
            except Exception as e:
                logger.error(f"RAG Corruption detected: {e}")
                backup = rag_file + ".bak"
                import shutil
                shutil.copy2(rag_file, backup)
                os.remove(rag_file)
                self.repair_log.append("Reset corrupted RAG memory store (Backup created).")

    def _verify_environment_integrity(self):
        if not settings.STRIPE_API_KEY or "placeholder" in settings.STRIPE_API_KEY:
            self.repair_log.append("⚠️ MONETIZATION: Stripe Key is MISSING. Falling back to test mode.")
        if not settings.GROQ_API_KEY:
            self.repair_log.append("⚠️ INTELLIGENCE: Groq Key is MISSING. LLM will be in mock mode.")

# Singleton
sovereign_healer = SelfHealingService()
