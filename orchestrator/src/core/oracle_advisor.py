import json
import os
import sys
import logging
from typing import Dict, List

# Ensure orchestrator is in path
sys.path.append(os.getcwd())

from orchestrator.src.logging.logger import get_logger
from orchestrator.src.core.llm_provider import llm_provider

logger = get_logger("ORACLE_ADVISOR")

CLICK_DATA = "data/customers/clicks.json"
STRATEGY_FILE = "data/governance/current_strategy.json"

class OracleAdvisor:
    """The High-Level Strategic Brain of the Sovereign Swarm."""
    
    def analyze_performance(self) -> Dict:
        logger.info("🔮 ORACLE: ANALYZING NEURAL FEEDBACK...")
        if not os.path.exists(CLICK_DATA):
            return {"best_channel": "email", "sentiment": "neutral"}
            
        with open(CLICK_DATA, "r") as f:
            clicks = json.load(f)
            
        if not clicks:
            return {"best_channel": "email", "sentiment": "neutral"}
            
        # Determine winning channel
        best_channel = max(clicks, key=clicks.get).split("_")[0]
        total_clicks = sum(clicks.values())
        
        logger.info(f"🔮 ORACLE: Channel '{best_channel}' is dominating with {total_clicks} events.")
        return {"best_channel": best_channel, "total_clicks": total_clicks}

    def generate_new_directives(self, performance: Dict):
        """Generates a high-level strategic directive for the next execution cycle."""
        prompt = (
            f"Current Performance: {performance}\n"
            "The Sovereign Swarm is currently monetizing 13 streams. "
            "Based on the performance data, write 3 'Directives' for the agents. "
            "Directives must be aggressive, revenue-focused, and use high-level military/tech terminology. "
            "Example: 'Phase 2: Saturate the IndieHackers sector with high-stakes SaaS pitches.'"
        )
        
        try:
            directives = llm_provider.generate_text(prompt)
            strategy = {
                "directives": directives,
                "target_channel": performance["best_channel"],
                "timestamp": str(os.times())
            }
            
            os.makedirs("data/governance", exist_ok=True)
            with open(STRATEGY_FILE, "w") as f:
                json.dump(strategy, f, indent=2)
                
            logger.info(f"🔮 ORACLE: NEW STRATEGIC DIRECTIVES ISSUED.")
            return directives
        except Exception as e:
            logger.error(f"Oracle Fail: {e}")
            return "Execute with maximum aggression."

if __name__ == "__main__":
    oracle = OracleAdvisor()
    perf = oracle.analyze_performance()
    oracle.generate_new_directives(perf)
