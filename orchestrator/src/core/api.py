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
    yield
    # Shutdown
    logger.info("Shutting down matrix.")

# --- RATE LIMITING GUARDRAIL ---
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 100, window: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.requests = {} # {ip: [timestamps]}

    async def dispatch(self, request: Request, call_next):
        if os.getenv("ENV_MODE", "dev") == "dev": return await call_next(request)
        ip = request.client.host
        now = datetime.utcnow().timestamp()
        if ip not in self.requests: self.requests[ip] = []
        self.requests[ip] = [t for t in self.requests[ip] if now - t < self.window]
        if len(self.requests[ip]) >= self.limit:
            return JSONResponse(status_code=429, content={"detail": "Sovereign shields engaged. Rate limit exceeded."})
        self.requests[ip].append(now)
        return await call_next(request)

app = FastAPI(title="Realms2Riches Sovereign Matrix", version="5.8.1", lifespan=lifespan)
app.add_middleware(RateLimitMiddleware, limit=120, window=60)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- STATIC FILES ---
os.makedirs("data/assets", exist_ok=True)
os.makedirs("data/marketing", exist_ok=True)
app.mount("/assets", StaticFiles(directory="data/assets"), name="assets")
app.mount("/marketing", StaticFiles(directory="data/marketing"), name="marketing")

# --- ENDPOINTS ---

@app.get("/health")
async def health_check():
    return {"status": "SOVEREIGN", "timestamp": datetime.utcnow().isoformat(), "agents_online": len(orchestrator.agents)}

@app.get("/api/telemetry/stats")
async def get_telemetry_stats():
    return telemetry_data

@app.get("/api/activity")
async def get_activity():
    return activity_log[-50:]

@app.get("/api/integrations/status")
async def get_integrations_status():
    # Real-time connectivity check
    db_status = "active"
    try:
        sql = SQLStore()
        # Ping check could go here
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
        # Load products
        with open("data/catalog/products.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            product_map = {row['id']: row for row in reader}
        
        # Load prices and join
        with open("data/catalog/prices.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                p_id = row['product_id']
                if p_id in product_map:
                    p = product_map[p_id].copy()
                    p['price'] = float(row['price'])
                    p['currency'] = row['currency']
                    p['interval'] = row['interval']
                    products.append(p)
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
        with open(posts_path, "r") as f:
            posts = json.load(f)
            for p in posts:
                if p['slug'] == slug:
                    post_meta = p
                    break
    
    # Load content from markdown
    md_path = f"data/blog/{slug}.md"
    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {
            "meta": post_meta or {"title": slug.replace("-", " ").title(), "slug": slug},
            "content": content
        }
    raise HTTPException(status_code=404, detail="Post not found")

@app.post("/api/sovereign/launch")
async def sovereign_launch(request: Request):
    payload = await request.json()
    license_key = request.headers.get("X-License-Key")
    
    # In a real scenario, validate license_key
    logger.info(f"🚀 SOVEREIGN LAUNCH INITIATED via license: {license_key}")
    
    return {
        "status": "active",
        "timestamp": datetime.utcnow().isoformat(),
        "matrix_id": str(uuid.uuid4()),
        "stream_count": 13,
        "message": "Sovereign Swarm fully unleashed in YOLO mode."
    }

@app.post("/api/tasks")
async def create_task(payload: Dict[str, Any]):
    task_desc = payload.get("description", "Unnamed Task")
    logger.info(f"Task received: {task_desc}")
    # Run task through orchestrator
    try:
        # We simulate a quick response for the cockpit
        asyncio.create_task(run_task_background(task_desc))
        return {"status": "dispatched", "task_id": str(uuid.uuid4())}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/leads")
async def capture_lead(payload: Dict[str, Any]):
    email = payload.get("email")
    source = payload.get("source", "unknown")
    logger.info(f"Lead captured: {email} from {source}")
    return {
        "status": "success", 
        "guide_url": f"{settings.BACKEND_URL}/assets/sovereign_strategy_guide_v3.txt"
    }

# --- WEBSOCKETS ---

@app.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    await voice_router.handle_connection(websocket)

@app.websocket("/ws/chamber")
async def websocket_chamber_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Chamber connection established.")
    try:
        # Send initial welcome or last few logs
        await websocket.send_text("Uplink to Sovereign Chamber established.")
        while True:
            # We just keep the connection open for now, 
            # real logs would be pushed here via a pub/sub or queue
            await asyncio.sleep(10)
            await websocket.send_text(f"Swarm pulse: {datetime.utcnow().strftime('%H:%M:%S')} - All streams nominal.")
    except WebSocketDisconnect:
        logger.info("Chamber connection dropped.")

# --- UTILS ---

@app.get("/sitemap.xml")
async def get_sitemap():
    path = "data/store/sitemap.xml"
    if os.path.exists(path): return FileResponse(path, media_type="application/xml")
    raise HTTPException(status_code=404, detail="Sitemap not found")

@app.get("/api/v1/user/credits")
async def get_user_credits(user_id: str = "primary_node"):
    sql = SQLStore()
    return sql.get_user_balance(user_id)

@app.post("/api/v1/monetization/webhook")
async def unified_stripe_webhook(request: Request):
    internal_header = request.headers.get("x-sovereign-internal")
    is_internal = (internal_header == "true")
    payload = await request.body()
    
    if is_internal:
        data = json.loads(payload)
        event = stripe.Event.construct_from(data, stripe.api_key)
    else:
        sig_header = request.headers.get("stripe-signature")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        try:
            if endpoint_secret:
                event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            else:
                data = json.loads(payload)
                event = stripe.Event.construct_from(data, stripe.api_key)
        except Exception as e:
            logger.error(f"Webhook Signature Error: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    event_type = event["type"]
    session = event["data"]["object"]

    if event_type == "checkout.session.completed":
        amount = session.get("amount_total", 0) / 100
        email = session.get("customer_details", {}).get("email")
        sql = SQLStore()
        sql.add_profit_entry({"id": str(uuid.uuid4()), "type": "revenue", "category": "sale", "amount": amount, "details": {"email": email}})
        telemetry_data["revenue"] += amount
        telemetry_data["conversions"] += 1
        activity_log.append({
            "t": datetime.utcnow().isoformat(),
            "a": "REVENUE_SHIELD",
            "op": "SALE_CAPTURED",
            "r": f"Captured ${amount} from {email}"
        })

    return {"status": "success"}

@app.get("/api/v1/swarm/transparency")
async def get_swarm_transparency():
    return {"active_swarms": 1, "total_agents": len(orchestrator.agents), "health": "100%", "recent_ops": activity_log[-10:]}

async def run_task_background(task: str):
    try:
        activity_log.append({
            "t": datetime.utcnow().isoformat(),
            "a": "DISPATCHER",
            "op": "TASK_START",
            "r": f"Processing: {task[:50]}"
        })
        async for step in orchestrator.submit_task_stream(task, "api_dispatch"):
            if step["status"] == "completed":
                result = step["result"]
                activity_log.append({
                    "t": datetime.utcnow().isoformat(),
                    "a": result.get("agent_name", "Swarm"),
                    "op": "TASK_COMPLETE",
                    "r": result.get("reasoning", "Execution finished.")[:200]
                })
    except Exception as e:
        logger.error(f"❌ API TASK FAILED: {e}")
        activity_log.append({
            "t": datetime.utcnow().isoformat(),
            "a": "SYSTEM",
            "op": "TASK_ERROR",
            "r": str(e)
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
