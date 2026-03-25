import asyncio
import os
import sys
import subprocess

# Ensure orchestrator is in path
sys.path.append(os.getcwd())

from orchestrator.src.logging.logger import get_logger
from orchestrator.src.core.oracle_advisor import OracleAdvisor

logger = get_logger("SOVEREIGN_FINALITY")

async def sovereign_finality_loop():
    """
    The Ultimate Execution Loop.
    1. Analyze (Oracle)
    2. React (Trend Jacker)
    3. Scale (Blitz)
    4. Verify (Evidence)
    """
    oracle = OracleAdvisor()
    
    print("\n" + "="*60)
    print("🚀 INITIALIZING SOVEREIGN FINALITY: THE ABSOLUTE BEST")
    print("="*60 + "\n")

    # STEP 1: NEURAL STRATEGY
    perf = oracle.analyze_performance()
    directives = oracle.generate_new_directives(perf)
    print(f"🔮 ORACLE DIRECTIVES:\n{directives}\n")

    # STEP 2: REAL-TIME TREND JACKING
    print("🕵️  DEPLOYING TREND JACKERS...")
    subprocess.run([sys.executable, "scripts/trend_jacking_swarm.py"])

    # STEP 3: HIGH-VELOCITY BLITZ (Optimized for the winning channel)
    print(f"🔥  EXECUTING BLITZ ON WINNING VECTOR: {perf['best_channel'].upper()}...")
    subprocess.run([sys.executable, "scripts/high_velocity_blitz.py"])

    # STEP 4: CAPTURE EVIDENCE
    print("📸  LOGGING VISUAL EVIDENCE...")
    subprocess.run([sys.executable, "scripts/capture_swarm_evidence.py"])

    # STEP 5: FINAL REPORT
    print("\n" + "="*60)
    print("🏆 SOVEREIGN FINALITY CYCLE COMPLETE")
    print("📍 EVIDENCE: data/marketing/evidence/")
    print("📊 DASHBOARD: data/marketing/swarm_visualization.html")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(sovereign_finality_loop())
