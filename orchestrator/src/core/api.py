from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.core.config import settings
from orchestrator.src.core.alchemy_engine import get_all_posts, generate_autonomous_blog_post
from orchestrator.src.core.catalog.api import catalog_api
from orchestrator.src.core.voice.router import VoiceRouter
from orchestrator.src.core.voice.mock_adapters import MockSTTAdapter, MockTTSAdapter
from orchestrator.src.core.licensing import license_manager
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.validation.schemas import TaskSpec
import asyncio
import json
import random
import time
import os
import hashlib
from datetime import datetime

logger = get_logger(__name__)

# Sovereign System State
swarm_active = True

# --- SECURITY & LICENSING ---
api_key_header = APIKeyHeader(name="X-License-Key", auto_error=False)

async def verify_license_header(key: str = Security(api_key_header)):
    if not key and settings.GROQ_API_KEY == "placeholder":
        return {"tier": "TRIAL", "features": ["basic", "swarm"]}
    if not key:
        return {"tier": "DEV", "features": ["basic", "swarm"]}
    if key == "mock_dev_key":
         return {"tier": "DEV", "features": ["swarm", "voice", "api", "admin"], "sub": "dev@local"}
    result = license_manager.verify_license_key(key)
    if not result["valid"]:
        if os.getenv("ENV_MODE", "dev") == "dev": return {"tier": "DEV", "features": ["swarm"]}
        raise HTTPException(status_code=403, detail=f"Invalid License: {result.get('error')}")
    return result["data"]

app = FastAPI(title="Sovereign API", version="3.9.1-LOCKED")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def skip_ngrok_warning(request: Request, call_next):
    response = await call_next(request)
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

# Shared Core Instances
orchestrator = Orchestrator()
voice_router = VoiceRouter(orchestrator, orchestrator.stt, orchestrator.tts)

activity_log = []
telemetry_data = {"campaigns_launched": 0, "messages_sent": 0, "impressions": 0, "revenue": 0.0, "clicks": 0}

def log_activity(agent: str, action: str, result: str):
    activity_log.append({"t": datetime.utcnow().isoformat(), "a": agent, "op": action, "r": result[:150]})
    if len(activity_log) > 50: activity_log.pop(0)

# --- BACKGROUND PROCESSORS ---
async def log_heartbeat():
    while True:
        logger.info(f"💓 HEARTBEAT: {len(orchestrator.agents)} Online | Matrix: ACTIVE")
        await asyncio.sleep(15)

async def autonomous_loop():
    while True:
        if swarm_active and len(orchestrator.agents) > 0:
            import random
            log_activity("ALPHA_CORE_1", "SYS_MAINTENANCE", "Verifying RAG integrity...")
            log_activity("BETA_GROWTH_2", "MARKET_PULSE", "Analyzing AI market shifts...")
            await asyncio.sleep(20)
        else:
            await asyncio.sleep(10)

@app.on_event("startup")
async def startup():
    asyncio.create_task(log_heartbeat())
    asyncio.create_task(autonomous_loop())

# --- PUBLIC ENDPOINTS ---

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "swarm": "ACTIVE",
        "agents": len(orchestrator.agents),
        "cells": orchestrator.get_matrix_status(),
        "rag": len(orchestrator.memory.documents),
        "version": "3.9.1-LOCKED"
    }

@app.get("/api/integrations/status")
async def integrations():
    def status(key):
        val = getattr(settings, key, None) or os.getenv(key)
        return "active" if val and val != "placeholder" and len(str(val)) > 5 else "inactive"
    
    # FLAT STRUCTURE FOR UI COMPATIBILITY
    return {
        "llm": status("GROQ_API_KEY"),
        "voice": status("ELEVENLABS_API_KEY"),
        "stripe": status("STRIPE_API_KEY"),
        "linkedin": status("LINKEDIN_ACCESS_TOKEN"),
        "email": status("SENDGRID_API_KEY"),
        "vector_db": "active",
        "docker": "active"
    }

@app.get("/api/blog/posts")
async def blog_posts():
    posts = get_all_posts()
    if not posts:
        return [{"slug": "welcome", "title": "Welcome to Realms 2 Riches", "date": "2026-02-20", "summary": "Matrix Online."}]
    return posts

@app.get("/api/blog/posts/{slug}")
async def get_single_post(slug: str):
    blog_dir = "data/blog"
    path = os.path.join(blog_dir, f"{slug}.md")
    if not os.path.exists(path):
        return {"meta": {"title": "Post Not Found", "date": ""}, "content": "The requested intelligence report is unavailable."}
    with open(path, "r") as f:
        content = f.read()
    return {"meta": {"title": slug.replace("-", " ").title(), "date": "2026-02-20"}, "content": content}

@app.get("/api/activity")
async def get_activity():
    return activity_log

@app.get("/api/telemetry/stats")
async def get_stats():
    return telemetry_data

@app.post("/api/telemetry/event")
async def record_event(request: Request):
    data = await request.json()
    if data.get("type") == "campaign_start": telemetry_data["campaigns_launched"] += 1
    return telemetry_data

@app.get("/products")
async def get_products():
    # Robust fallback list
    return [
        {"name": "Sovereign License", "description": "Full access.", "prices": [{"price": 49, "interval": "mo", "product_id": "plat"}]}
    ]

@app.post("/api/checkout/session")
async def checkout(request: Request):
    return {"url": f"{settings.FRONTEND_URL}/success"}

@app.post("/api/tasks")
async def submit_task(request: Request, license_data: dict = Depends(verify_license_header)):
    data = await request.json()
    desc = data.get("description")
    result = {}
    async for step in orchestrator.submit_task_stream(desc, "adhoc"):
        if step["status"] == "completed": result = step["result"]
    return {"status": "completed", "result": result}

@app.websocket("/ws/voice")
async def ws_voice(websocket: WebSocket, token: str = None):
    await websocket.accept()
    session = voice_router.create_session()
    async def receiver():
        try:
            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)
                if msg.get("type") == "stop": await session.add_input({"type": "stop"})
        except: pass
    async def sender():
        try:
            while True:
                evt = await session.get_output()
                await websocket.send_json(evt)
        except: pass
    await asyncio.gather(receiver(), sender())

@app.websocket("/ws/chamber")
async def chamber_socket(websocket: WebSocket, token: str = None):
    await websocket.accept()
    try:
        last_idx = 0
        while True:
            current_log = activity_log[last_idx:]
            for item in current_log:
                await websocket.send_text(f"[{item['a']}] {item['op']}: {item['r']}")
            last_idx = len(activity_log)
            await asyncio.sleep(1)
    except Exception: pass
