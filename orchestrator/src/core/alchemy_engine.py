import os
import json
import re
from datetime import datetime
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

def parse_markdown_metadata(content: str) -> dict:
    """Extracts yaml-like frontmatter from markdown strings."""
    meta = {}
    match = re.search(r'---\s+(.*?)\s+---', content, re.DOTALL)
    if match:
        lines = match.group(1).split('\n')
        for line in lines:
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip()] = v.strip().strip('"')
    return meta

def get_all_posts(blog_dir: str = "data/blog"):
    posts = []
    if not os.path.exists(blog_dir): return posts
    
    for filename in os.listdir(blog_dir):
        if filename.endswith(".md"):
            with open(os.path.join(blog_dir, filename), 'r', encoding='utf-8') as f:
                content = f.read()
                meta = parse_markdown_metadata(content)
                posts.append({
                    "slug": filename.replace(".md", ""),
                    "title": meta.get("title", filename),
                    "date": meta.get("date", "2026-02-20"),
                    "summary": meta.get("summary", "Autonomous report."),
                    "tags": meta.get("tags", [])
                })
    return sorted(posts, key=lambda x: x['date'], reverse=True)

def generate_autonomous_blog_post(task_result: dict):
    blog_dir = "data/blog"
    os.makedirs(blog_dir, exist_ok=True)
    slug = f"report-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    
    content = f"""---
title: "Neural Pulse: {task_result.get('agent_id', 'Swarm Analysis')}"
date: "{datetime.utcnow().strftime('%Y-%m-%d')}"
summary: "System-generated analysis of recent agent workstreams."
---

# Swarm Intelligence Update

Recent task execution in the Sovereign Matrix has yielded the following architectural insights:

{task_result.get('reasoning', 'No reasoning provided.')}

Verified by TITAN ORCHESTRATOR.
"""
    with open(os.path.join(blog_dir, f"{slug}.md"), 'w') as f:
        f.write(content)
    return slug
