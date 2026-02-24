import time
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TelemetryCollector:
    """
    Industry-standard Observability Layer.
    Tracks latency, token usage, and conversion metrics in real-time.
    """
    def __init__(self):
        self.spans = []

    def start_span(self, name: str, agent_id: str, trace_id: str):
        return {
            "name": name,
            "agent_id": agent_id,
            "trace_id": trace_id,
            "start_time": time.time(),
            "status": "RUNNING"
        }

    def end_span(self, span: Dict[str, Any], status: str = "SUCCESS", metadata: Optional[Dict[str, Any]] = None):
        span["end_time"] = time.time()
        span["duration_ms"] = (span["end_time"] - span["start_time"]) * 1000
        span["status"] = status
        span["timestamp"] = datetime.utcnow().isoformat()
        if metadata: span.update(metadata)
        
        # Log as structured JSON for easy ELK/Datadog ingestion
        logger.info(f"📊 TELEMETRY | {json.dumps(span)}")
        self.spans.append(span)
        if len(self.spans) > 1000: self.spans.pop(0)

    def get_aggregate_stats(self) -> Dict[str, Any]:
        if not self.spans: return {"status": "NO_DATA"}
        
        total_duration = sum(s["duration_ms"] for s in self.spans)
        avg_latency = total_duration / len(self.spans)
        success_rate = sum(1 for s in self.spans if s["status"] == "SUCCESS") / len(self.spans)
        
        return {
            "avg_latency_ms": round(avg_latency, 2),
            "success_rate": f"{round(success_rate * 100, 2)}%",
            "total_signals": len(self.spans)
        }

# Singleton instance for the matrix
telemetry = TelemetryCollector()
