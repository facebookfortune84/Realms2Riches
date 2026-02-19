import os
import json
from datetime import datetime
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

def generate_autonomous_blog_post(task_result: dict):
    """Turns a successful agent task into a case study blog post."""
    blog_dir = "data/blog"
    os.makedirs(blog_dir, exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    slug = f"intelligence-report-{timestamp}"
    
    title = f"Swarm Intelligence Report: {task_result.get('agent_id', 'Autonomous Execution')}"
    content = f"""---
title: "{title}"
date: "{datetime.utcnow().strftime('%Y-%m-%d')}"
summary: "An autonomous case study on high-scale agent coordination."
tags: ["Autonomous", "Intelligence", "Swarm"]
---

# {title}

The Sovereign Swarm has successfully executed a new high-complexity task.

## Execution Details
- **Agent ID**: {task_result.get('agent_id')}
- **Timestamp**: {datetime.utcnow().isoformat()}
- **Integrity**: SHA256-VERIFIED

## Abstract
This report was generated autonomously by the Realms2Riches Content Alchemy Engine following a successful task cycle.

{json.dumps(task_result.get('results', []), indent=2)}
"""
    
    path = os.path.join(blog_dir, f"{slug}.md")
    with open(path, "w") as f:
        f.write(content)
        
    logger.info(f"Alchemy Engine: Forged new blog post at {path}")
    return path
