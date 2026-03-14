from typing import Dict, Any, List
from orchestrator.src.tools.base import BaseTool, ToolConfig
import requests
import os
import json
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class SystemAuditTool(BaseTool):
    """
    Grand Wizard Audit Tool.
    Systematically hits every major endpoint and verifies data integrity.
    """
    
    ENDPOINTS = [
        "/health",
        "/products",
        "/api/telemetry/stats",
        "/api/integrations/status",
        "/api/activity"
    ]

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        base_url = settings.BACKEND_URL
        results = {}
        total_tests = len(self.ENDPOINTS)
        passed = 0

        for ep in self.ENDPOINTS:
            try:
                res = requests.get(f"{base_url}{ep}", timeout=2)
                status = "PASS" if res.status_code == 200 else f"FAIL ({res.status_code})"
                if res.status_code == 200: passed += 1
                results[ep] = {
                    "status": status,
                    "response_time_ms": res.elapsed.total_seconds() * 1000,
                    "payload_size": len(res.text)
                }
            except Exception as e:
                results[ep] = {"status": f"ERROR ({str(e)})"}

        # Custom Integrity Checks
        results["DATA_SLOTS"] = "PASS" if os.path.exists("data/store/slots/baseline.json") else "FAIL"
        results["STRATEGY_GUIDE"] = "PASS" if os.path.exists("data/assets/sovereign_strategy_guide_v3.txt") else "FAIL"
        
        score = (passed / total_tests) * 100

        return {
            "status": "completed",
            "score": f"{score}%",
            "endpoint_audit": results,
            "system_health": "ALIGNED" if score == 100 else "DEVIATED"
        }

class SelfHealingOptimizationTool(BaseTool):
    """
    Fallback/Optimization Tool.
    Triggered when CELL_DELTA detects a deviation.
    """
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        issue = params.get("issue", "Unknown deviation")
        logger.warning(f"🛡️ SELF-HEALING TRIGGERED for: {issue}")
        
        # 1. Run Healer Service
        from orchestrator.src.core.self_healing import sovereign_healer
        repairs = sovereign_healer.execute_healing_cycle()
        
        return {
            "status": "success",
            "action": "Applied environmental repairs",
            "repairs_performed": repairs,
            "state": "RECOVERED"
        }
