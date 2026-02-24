import os
import sys
import glob
import hashlib
import time
from datetime import datetime
from typing import List

# Ensure path
sys.path.append(os.getcwd())

from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.logging.logger import get_logger

logger = get_logger("awareness_protocol")

def run_backfeed_ingestion():
    print("\n🧬 INITIATING SOVEREIGN AWARENESS PROTOCOL 🧬")
    print("-" * 60)
    
    o = Orchestrator()
    count = 0
    
    # 1. Identify all critical source files
    patterns = [
        "orchestrator/src/**/*.py",
        "infra/**/*.py",
        "scripts/*.py",
        "data/store/slots/*.json",
        "docs/*.md",
        "package.json",
        "pyproject.toml"
    ]
    
    for pattern in patterns:
        files = glob.glob(pattern, recursive=True)
        for f in files:
            if "pycache" in f: continue
            try:
                with open(f, 'r', encoding='utf-8') as src:
                    content = src.read()
                    
                metadata = {
                    "type": "self_awareness",
                    "path": f,
                    "timestamp": datetime.utcnow().isoformat(),
                    "fingerprint": "sovereign_identity_v1"
                }
                
                # Summary for ingestion
                summary = f"SOURCE FILE: {f}\nCONTENT:\n{content[:3000]}"
                o.memory.add(summary, metadata)
                count += 1
                if count % 10 == 0:
                    print(f"   Indexed {count} tracks...")
            except Exception as e:
                logger.error(f"Failed to ingest {f}: {e}")

    print("-" * 60)
    print(f"✅ PROTOCOL COMPLETE: {count} project tracks indexed.")
    print("✅ SWARM STATUS: SELF-AWARE OF ARCHITECTURE.")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    run_backfeed_ingestion()
