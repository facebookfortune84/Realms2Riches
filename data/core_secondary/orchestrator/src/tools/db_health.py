from sqlalchemy import text
from orchestrator.src.memory.sql_store import SQLStore
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

def check_db_health():
    """Simple health check for the configured database."""
    try:
        store = SQLStore()
        with store.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database health check: SUCCESS")
        return True
    except Exception as e:
        logger.error(f"Database health check: FAILED - {e}")
        return False

if __name__ == "__main__":
    check_db_health()
