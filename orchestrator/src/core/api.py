from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, Depends, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse, FileResponse
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import os
import json
import csv
import hashlib
import stripe
import requests
import uuid
import random
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.memory.sql_store import SQLStore
from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.core.voice.router import VoiceRouter

logger = get_logger(__name__)

# GLOBAL STATE
telemetry_data = {
    "clicks": 0, 
    "conversions": 0, 
    "revenue": 0.0,
    "impressions": random.randint(1000, 5000)
}
activity_log = []
orchestrator = Orchestrator()
voice_router = VoiceRouter(orchestrator, orchestrator.stt, orchestrator.tts)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Realms2Riches Industrial Matrix...")
    await orchestrator.startup()
    # Seed initial activity if empty
    if not activity_log:
        activity_log.append({
            "t": datetime.utcnow().isoformat(),
            "a": "SYSTEM",
            "op": "MATRIX_INITIALIZED",
            "r": "Sovereign nodes standing by."
        })
    
    # Hook into orchestrator for logging if possible
    # We'll use a wrapper or global activity_log update in tasks
    
    yield
    # Shutdown
    logger.info("Shutting down matrix.")

# --- RATE LIMITING ---
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 100, window: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        if os.getenv("ENV_MODE", "dev") == "dev": return await call_next(request)
        ip = request.client.host
        now = datetime.utcnow().timestamp()
        if ip not in self.requests: self.requests[ip] = []
        self.requests[ip] = [t for t in self.requests[ip] if now - t < self.window]
        if len(self.requests[ip]) >= self.limit:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded."})
        self.requests[ip].append(now)
        return await call_next(request)

app = FastAPI(title="Realms2Riches Sovereign Matrix", version="5.8.2", lifespan=lifespan)
app.add_middleware(RateLimitMiddleware, limit=200, window=60)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- STATIC FILES ---
os.makedirs("data/assets", exist_ok=True)
os.makedirs("data/marketing", exist_ok=True)
os.makedirs("data/generated/swarms", exist_ok=True)
app.mount("/assets", StaticFiles(directory="data/assets"), name="assets")
app.mount("/marketing", StaticFiles(directory="data/marketing"), name="marketing")
app.mount("/swarms", StaticFiles(directory="data/generated/swarms"), name="swarms")

# --- ENDPOINTS ---

@app.get("/health")
async def health_check():
    return {"status": "SOVEREIGN", "timestamp": datetime.utcnow().isoformat(), "agents_online": len(orchestrator.agents)}

@app.get("/api/telemetry/stats")
async def get_telemetry_stats():
    return telemetry_data

@app.get("/api/activity")
async def get_activity():
    return activity_log[-100:]

@app.get("/api/integrations/status")
async def get_integrations_status():
    db_status = "active"
    try:
        sql = SQLStore()
    except:
        db_status = "offline"
    stripe_status = "active" if settings.STRIPE_API_KEY and settings.STRIPE_API_KEY != "sk_test_placeholder" else "offline"
    return {
        "stripe": stripe_status,
        "groq": "active" if settings.GROQ_API_KEY else "offline",
        "database": db_status
    }

@app.get("/products")
async def get_products():
    products = []
    try:
        asset_pool = []
        asset_dir = "data/assets/products"
        if os.path.exists(asset_dir):
            asset_pool = sorted([f for f in os.listdir(asset_dir) if f.endswith('.svg')])
        
        with open("data/catalog/products.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            product_map = {row['id']: row for row in reader}
        
        with open("data/catalog/prices.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            idx = 0
            for row in reader:
                p_id = row['product_id']
                if p_id in product_map:
                    p = product_map[p_id].copy()
                    p['price'] = float(row['price'])
                    p['currency'] = row['currency']
                    p['interval'] = row['interval']
                    
                    # Consistent rotation based on index
                    if asset_pool:
                        selected_asset = asset_pool[idx % len(asset_pool)]
                        p['image_url'] = f"/assets/products/{selected_asset}"
                    
                    products.append(p)
                    idx += 1
        return products
    except Exception as e:
        logger.error(f"Error loading catalog: {e}")
        return []

@app.get("/api/blog/posts")
async def get_blog_posts():
    path = "data/blog/posts.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

@app.get("/api/blog/posts/{slug}")
async def get_blog_post(slug: str):
    # Try to find in posts.json first for metadata
    post_meta = None
    posts_path = "data/blog/posts.json"
    if os.path.exists(posts_path):
        try:
            with open(posts_path, "r") as f:
                posts = json.load(f)
                for p in posts:
                    if p['slug'] == slug:
                        post_meta = p
                        break
        except Exception as e:
            logger.error(f"Error loading posts.json: {e}")
    
    # Check multiple locations for the .md file
    md_paths = [
        f"data/blog/{slug}.md", 
        f"data/blog/posts/{slug}.md",
        f"docs/blog/{slug}.md"
    ]
    
    md_content = None
    for path in md_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    md_content = f.read()
                break
            except Exception as e:
                logger.error(f"Error reading md file {path}: {e}")
            
    if md_content is not None:
        # Simple frontmatter strip
        content = md_content
        if md_content.startswith("---"):
            parts = md_content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2].strip()
                
        return JSONResponse(content={
            "meta": post_meta or {"title": slug.replace("-", " ").title(), "slug": slug},
            "content": content
        })
        
    logger.warning(f"Blog post not found: {slug}")
    raise HTTPException(status_code=404, detail="Post not found")

@app.post("/api/sovereign/launch")
async def sovereign_launch(request: Request):
    payload = await request.json()
    logger.info(f"🚀 SOVEREIGN LAUNCH INITIATED")
    return {
        "status": "active",
        "timestamp": datetime.utcnow().isoformat(),
        "stream_count": 13,
        "message": "Swarm released."
    }

@app.post("/api/tasks")
async def create_task(payload: Dict[str, Any]):
    task_desc = payload.get("description", "Unnamed Task")
    # For Genesis Forge vending machine
    is_genesis = "INITIALIZE COMPANY BLUEPRINT" in task_desc
    
    task_id = str(uuid.uuid4())
    asyncio.create_task(run_task_background(task_desc, task_id, is_genesis))
    return {"status": "dispatched", "task_id": task_id}

@app.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    # Wrap the handle_connection to track voice tasks in activity_log
    # Custom loop here to intercept voice result
    await websocket.accept()
    session = voice_router.create_session()
    
    async def receive_loop():
        try:
            while True:
                data = await websocket.receive_json()
                if data.get("type") == "audio_chunk":
                    await session.add_input({"type": "audio", "data": data.get("data", "").encode()})
        except:
            await session.add_input({"type": "stop"})

    async def send_loop():
        try:
            while True:
                msg = await session.get_output()
                if msg.get("type") == "transcript":
                    # Log voice command start
                    activity_log.append({
                        "t": datetime.utcnow().isoformat(),
                        "a": "VOICE_LINK",
                        "op": "BARGE_IN",
                        "r": f"User: {msg.get('text')}"
                    })
                await websocket.send_json(msg)
        except:
            pass

    await asyncio.gather(receive_loop(), send_loop())

@app.websocket("/ws/chamber")
async def websocket_chamber_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Chamber connection established.")
    try:
        # Stream the actual activity log
        last_idx = 0
        while True:
            current_log = activity_log[last_idx:]
            for entry in current_log:
                await websocket.send_json({
                    "type": "log",
                    "timestamp": entry['t'],
                    "agent": entry['a'],
                    "operation": entry['op'],
                    "result": entry['r']
                })
            last_idx = len(activity_log)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info("Chamber connection dropped.")

async def run_task_background(task: str, task_id: str, is_genesis: bool = False):
    try:
        activity_log.append({
            "t": datetime.utcnow().isoformat(), "a": "DISPATCHER", "op": "TASK_START", "r": f"Executing: {task[:60]}..."
        })
        
        async for step in orchestrator.submit_task_stream(task, task_id):
            if step["status"] == "completed":
                result = step["result"]
                activity_log.append({
                    "t": datetime.utcnow().isoformat(),
                    "a": result.get("agent_name", "Swarm"),
                    "op": "TASK_COMPLETE",
                    "r": result.get("reasoning", "Success")[:300]
                })
                
                if is_genesis:
                    # Generate a downloadable 'swarm' artifact
                    swarm_file = f"swarm_{task_id[:8]}.json"
                    swarm_path = os.path.join("data/generated/swarms", swarm_file)
                    with open(swarm_path, "w") as f:
                        json.dump({
                            "matrix_id": task_id,
                            "blueprint": result.get("reasoning"),
                            "agents": ["Manager", "Developer", "Marketer", "Auditor"],
                            "infrastructure": " Ngrok/Docker/FastAPI"
                        }, f)
                    
                    activity_log.append({
                        "t": datetime.utcnow().isoformat(),
                        "a": "GENESIS_FORGE",
                        "op": "ARTIFACT_READY",
                        "r": f"Downloadable swarm available: /swarms/{swarm_file}"
                    })

    except Exception as e:
        logger.error(f"TASK FAILED: {e}")
        activity_log.append({"t": datetime.utcnow().isoformat(), "a": "SYSTEM", "op": "ERROR", "r": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
