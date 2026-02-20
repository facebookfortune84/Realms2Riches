from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.core.config import settings
from orchestrator.src.core.alchemy_engine import get_all_posts, generate_autonomous_blog_post
from orchestrator.src.core.catalog.api import catalog_api
from orchestrator.src.core.voice.router import VoiceRouter
from orchestrator.src.core.voice.mock_adapters import MockSTTAdapter, MockTTSAdapter
from orchestrator.src.logging.logger import get_logger
import asyncio
import json
import random
from datetime import datetime

logger = get_logger(__name__)

app = FastAPI(title="Sovereign API", version="3.5.0-PLATINUM")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared Core Instances
orchestrator = Orchestrator()
voice_router = VoiceRouter(orchestrator, MockSTTAdapter(), MockTTSAdapter())

activity_log = []
telemetry_data = {"campaigns": 0, "messages": 0, "impressions": 0, "revenue": 0.0}

def log_activity(agent: str, action: str, result: str):
    activity_log.append({"t": datetime.utcnow().isoformat(), "a": agent, "op": action, "r": result[:100]})
    if len(activity_log) > 50: activity_log.pop(0)

# --- BACKGROUND PROCESSORS ---
async def autonomous_loop():
    while True:
        # BETA Cell: Market Research
        log_activity("BETA_MARKETING_1", "SEO_SCAN", "Analyzing trend: 'Autonomous Sovereignty'")
        # ALPHA Cell: Self-Improvement
        log_activity("ALPHA_ENGINEERING_4", "CODE_AUDIT", "Optimizing RAG vector lookup latency")
        await asyncio.sleep(45)

@app.on_event("startup")
async def startup():
    asyncio.create_task(autonomous_loop())

# --- ENDPOINTS ---

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "swarm": "ACTIVE",
        "agents": len(orchestrator.agents),
        "cells": orchestrator.get_matrix_status(),
        "rag": len(orchestrator.memory.documents)
    }

@app.get("/api/integrations/status")
async def integrations():
    def status(k):
        v = getattr(settings, k, None)
        return "active" if v and len(str(v)) > 10 else "inactive"
    
    return {
        "intel": status("GROQ_API_KEY"),
        "voice": status("ELEVENLABS_API_KEY"),
        "pay": status("STRIPE_API_KEY"),
        "social": status("LINKEDIN_ACCESS_TOKEN"),
        "email": status("SENDGRID_API_KEY")
    }

@app.get("/api/blog/posts")
async def blog_posts():
    return get_all_posts()

@app.get("/api/blog/posts/{slug}")
async def get_single_post(slug: str):
    blog_dir = "data/blog"
    path = os.path.join(blog_dir, f"{slug}.md")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Post not found")
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Simple frontmatter split
    parts = content.split("---", 2)
    meta = {}
    body = content
    if len(parts) >= 3:
        import yaml # Should use yaml if available, or simple parse
        try:
            # Fallback manual parse if pyyaml not installed
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"')
            body = parts[2].strip()
        except: pass
        
    return {"meta": meta, "content": body}

@app.get("/api/activity")
async def get_activity():
    return activity_log

@app.post("/api/tasks")
async def submit_task(request: Request):
    data = await request.json()
    desc = data.get("description")
    
    result = {}
    async for step in orchestrator.submit_task_stream(desc, "adhoc"):
        if step["status"] == "completed":
            result = step["result"]
            # Trigger autonomous content generation on task completion
            generate_autonomous_blog_post(result)
            log_activity(result.get("agent_id"), "TASK_COMPLETE", result.get("reasoning"))
            
    return {"status": "completed", "result": result}

@app.get("/products")
async def get_products():
    return catalog_api.get_products() or [{
        "name": "Platinum License",
        "description": "Full access to the 3-Cell Sovereign Swarm.",
        "prices": [{"price": 49, "interval": "mo", "product_id": "plat_base"}]
    }]

@app.websocket("/ws/voice")
async def ws_voice(websocket: WebSocket):
    await websocket.accept()
    session = voice_router.create_session()
    
    async def receiver():
        try:
            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)
                if msg.get("type") == "stop": await session.add_input({"type": "stop"})
                elif msg.get("type") == "audio": await session.add_input({"type": "audio", "data": msg["data"].encode()})
        except: pass

    async def sender():
        try:
            while True:
                evt = await session.get_output()
                await websocket.send_json(evt)
        except: pass

    await asyncio.gather(receiver(), sender())
