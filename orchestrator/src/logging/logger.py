import logging
import json
import sys
import os
from datetime import datetime
from typing import Any, Dict

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
            "process": record.process,
        }
        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data) # type: ignore
        return json.dumps(log_record)

def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        # Standard stdout handler
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(JsonFormatter())
        logger.addHandler(stdout_handler)
        
        # Persistent file handler for deep auditing
        os.makedirs("data/logs", exist_ok=True)
        file_handler = logging.FileHandler(f"data/logs/swarm_activity.log")
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)
        
    return logger
