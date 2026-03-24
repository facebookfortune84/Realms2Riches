import os
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
SOURCE_DIR = Path(".")
DEST_DIR = Path("core_secondary")
IGNORE_PATTERNS = [
    ".git",
    ".github", # GitHub actions are for main repo only usually
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "core_secondary", # Avoid infinite recursion
    "dist",
    "build",
    ".idea",
    ".vscode",
    ".DS_Store",
    "Thumbs.db",
    "*.pyc",
    "*.log",
    "tmp",
    ".gemini"
]

def sync_core():
    """
    Synchronizes the root directory to core_secondary, acting as a 1:1 fallback.
    """
    logger.info(f"🔄 Starting Core Sync: {SOURCE_DIR.absolute()} -> {DEST_DIR.absolute()}")
    
    if not DEST_DIR.exists():
        DEST_DIR.mkdir(parents=True)
        logger.info(f"📁 Created destination directory: {DEST_DIR}")

    # Walk through source directory
    for root, dirs, files in os.walk(SOURCE_DIR):
        # Convert to Path object
        current_path = Path(root)
        
        # Calculate relative path from source
        rel_path = current_path.relative_to(SOURCE_DIR)
        
        # Skip if the path starts with ignored directories
        if any(str(rel_path).startswith(p) or str(rel_path) == p for p in IGNORE_PATTERNS):
            continue
            
        # Modify dirs in-place to prevent walking into ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_PATTERNS]
        
        # Determine destination directory
        dest_path = DEST_DIR / rel_path
        
        # Create destination directory if it doesn't exist
        if not dest_path.exists():
            dest_path.mkdir(parents=True, exist_ok=True)
            # logger.info(f"📁 Created: {dest_path}")
            
        # Copy files
        for file in files:
            # Check if file matches ignore patterns
            if any(file.endswith(p.replace("*", "")) for p in IGNORE_PATTERNS if "*" in p) or file in IGNORE_PATTERNS:
                continue
                
            src_file = current_path / file
            dest_file = dest_path / file
            
            # Check if file needs updating (size or mtime)
            if not dest_file.exists() or src_file.stat().st_mtime > dest_file.stat().st_mtime:
                try:
                    shutil.copy2(src_file, dest_file)
                    logger.info(f"✅ Synced: {rel_path / file}")
                except PermissionError:
                    logger.warning(f"⚠️ Permission denied: {src_file}")
                except Exception as e:
                    logger.error(f"❌ Error syncing {src_file}: {e}")

    logger.info("🏁 Core Sync Complete.")

if __name__ == "__main__":
    sync_core()
