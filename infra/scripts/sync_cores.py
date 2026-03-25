import os
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CORE_SYNC")

# Configuration
SOURCE_CORE = "orchestrator/src"
TARGET_CORE = "core_secondary/orchestrator/src"
SYNC_DIRECTORIES = ["agents", "core", "logging", "memory", "tools", "validation"]

def sync_cores():
    """
    Synchronizes the primary orchestrator logic to the secondary/fallback core.
    Ensures that self-healing and redundancy are always based on the latest codebase.
    """
    logger.info("🔄 INITIATING CORE SYNCHRONIZATION...")
    
    if not os.path.exists("core_secondary"):
        logger.error("❌ core_secondary directory not found. Sync aborted.")
        return

    for directory in SYNC_DIRECTORIES:
        src_path = os.path.join(SOURCE_CORE, directory)
        dest_path = os.path.join(TARGET_CORE, directory)
        
        if os.path.exists(src_path):
            logger.info(f"  -> Syncing: {directory}...")
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(src_path, dest_path)
        else:
            logger.warning(f"  -> Source directory not found: {src_path}")

    # Also sync relevant scripts
    scripts_src = "scripts"
    scripts_dest = "core_secondary/scripts"
    if os.path.exists(scripts_src):
        logger.info("  -> Syncing: scripts...")
        if os.path.exists(scripts_dest):
            shutil.rmtree(scripts_dest)
        shutil.copytree(scripts_src, scripts_dest)

    logger.info("✅ CORE SYNCHRONIZATION COMPLETE.")

if __name__ == "__main__":
    sync_cores()
