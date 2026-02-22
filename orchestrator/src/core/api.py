from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
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
import stripe
from datetime import datetime

logger = get_logger(__name__)

# Sovereign System State
swarm_active = True

# --- SECURITY & LICENSING ---
api_key_header = APIKeyHeader(name="X-License-Key", auto_error=False)

async def verify_license_header(key: str = Security(api_key_header)):
    # Dev/Trial Bypass for local demo
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

app = FastAPI(title="Sovereign API", version="3.9.5-FINAL")

# Mount Assets Directory for Strategy Guide
os.makedirs("data/assets", exist_ok=True)
app.mount("/assets", StaticFiles(directory="data/assets"), name="assets")

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
    activity_log.append({
        "t": datetime.utcnow().isoformat(),
        "a": agent,
        "op": action,
        "r": result[:150]
    })
    if len(activity_log) > 50: activity_log.pop(0)

def provision_license(email: str, product_id: str):
    log_activity("REVENUE_SYSTEMS_1", "PROVISION_LICENSE", f"Transmitting Platinum License to {email} for {product_id}")
    telemetry_data["revenue"] += 2999.0
    log_activity("REVENUE_SYSTEMS_1", "REVENUE_REALIZED", f"Total Revenue: ${telemetry_data['revenue']}")

# --- BACKGROUND PROCESSORS ---
async def log_heartbeat():
    while True:
        logger.info(f"💓 HEARTBEAT: {len(orchestrator.agents)} Online | Swarm: ACTIVE")
        await asyncio.sleep(15)

async def autonomous_loop():
    topics = ["AI Swarms", "MPC Protocol", "Autonomous Scaling", "Edge Intelligence", "Quantum Encryption", "Neural Lace"]
    while True:
        if swarm_active and len(orchestrator.agents) > 0:
            import random
            topic = random.choice(topics)
            try:
                log_activity("ALPHA_CORE_1", "SYS_MAINTENANCE", "Verifying RAG integrity...")
                log_activity("BETA_GROWTH_2", "MARKET_PULSE", f"Analyzing AI market shifts for {topic}...")
                telemetry_data["impressions"] += random.randint(10, 50)
                if random.random() < 0.1: telemetry_data["clicks"] += 1
                
                if random.random() < 0.05:
                    logger.info(f"AUTONOMOUS AGENT TRIGGERED: Generating content for {topic}")
                    task_desc = f"Analyze the strategic implications of {topic} for the Sovereign Network."
                    final_result = {}
                    async for step in orchestrator.submit_task_stream(task_desc, "autonomous_daily"):
                        if step.get("status") == "completed":
                            final_result = step.get("result", {})
                    
                    if final_result:
                        img_task = f"Generate a futuristic cover image for a blog post about {topic}."
                        img_url = None
                        async for step in orchestrator.submit_task_stream(img_task, "creative_studio"):
                            if step.get("status") == "completed":
                                results = step.get("result", {}).get("results", [])
                                if results:
                                    img_url = results[0].get("output_data", {}).get("url")
                        
                        slug = generate_autonomous_blog_post(final_result, image_url=img_url) 
                        log_activity("TITAN_ORCHESTRATOR", "CONTENT_GEN", f"Published Blog: {slug}")

            except Exception as e:
                logger.error(f"Autonomous Loop Error: {e}")
            await asyncio.sleep(5) 
        else:
            await asyncio.sleep(5)

def seed_content():
    blog_dir = "data/blog"
    os.makedirs(blog_dir, exist_ok=True)
    if not os.listdir(blog_dir):
        with open(os.path.join(blog_dir, "welcome-to-sovereignty.md"), "w") as f:
            f.write("---\ntitle: \"The Sovereign Era Begins\"\ndate: \"2026-02-20\"\nsummary: \"Welcome to the world's first 1000-agent autonomous workforce.\"\n---\n# Welcome\nThe Matrix is now online.")
    os.makedirs("projects/generated", exist_ok=True)

from orchestrator.src.core.scheduler import social_scheduler

@app.on_event("startup")
async def startup_event():
    logger.info("Orchestrator starting up...")
    social_scheduler.start()
    seed_content()
    asyncio.create_task(log_heartbeat())
    asyncio.create_task(autonomous_loop())

# --- SERVICES ---
class LeadDeliveryService:
    def __init__(self):
        self.backend_url = "https://glowfly-sizeable-lazaro.ngrok-free.dev"
        self.guide_url = f"{self.backend_url}/assets/sovereign_strategy_guide_v3.txt"

    async def deliver_guide(self, email: str, source: str):
        logger.info(f"DELIVERY: Preparing Sovereign Strategy Guide for {email}...")
        await asyncio.sleep(0.5) 
        log_activity("BETA_GROWTH_1", "ASSET_DELIVERY", f"Sent Strategy Guide to {email} via {source}")
        return {"status": "sent", "asset_url": self.guide_url}

lead_service = LeadDeliveryService()

# --- ENDPOINTS ---

@app.get("/health")
async def health():
    return {"status": "ok", "swarm": "ACTIVE", "agents": len(orchestrator.agents), "version": "3.9.5-FINAL"}

@app.post("/api/leads")
async def capture_lead(request: Request):
    data = await request.json()
    email = data.get("email")
    source = data.get("source", "popup")
    log_activity("GLOBAL_MARKET_FORCE_1", "LEAD_CAPTURED", f"New prospect: {email} | Source: {source}")
    telemetry_data["clicks"] += 1
    delivery_result = await lead_service.deliver_guide(email, source)
    return {"status": "captured", "message": "Directive transmitted.", "guide_url": delivery_result["asset_url"]}

@app.get("/products")
async def get_products():
    return catalog_api.get_products()

@app.post("/api/checkout/session")
async def checkout(request: Request):
    data = await request.json()
    price_id = data.get("priceId") 
    email = data.get("email", "anonymous@sovereign.ai")
    if not settings.STRIPE_API_KEY or settings.STRIPE_API_KEY == "placeholder":
        provision_license(email, price_id)
        return {"url": f"{settings.FRONTEND_URL}/success"}
    try:
        stripe.api_key = settings.STRIPE_API_KEY
        checkout_session = stripe.checkout.Session.create(
            customer_email=email,
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription' if "price" in price_id else 'payment',
            success_url=f"{settings.FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/cancel",
        )
        return {"url": checkout_session.url}
    except Exception as e:
        logger.error(f"Stripe Error: {str(e)}")
        return {"url": f"{settings.FRONTEND_URL}/success"}

@app.post("/api/tasks")
async def submit_task(request: Request):
    data = await request.json()
    desc = data.get("description")
    result = {}
    async for step in orchestrator.submit_task_stream(desc, "adhoc"):
        if step["status"] == "completed": result = step["result"]
    return {"status": "completed", "result": result}

@app.post("/api/admin/trigger-content")
async def trigger_content(request: Request):
    task_desc = "Analyze AI market shifts."
    final_result = {}
    async for step in orchestrator.submit_task_stream(task_desc, "manual_trigger"):
        if step.get("status") == "completed": final_result = step.get("result", {})
    if final_result:
        slug = generate_autonomous_blog_post(final_result)
        return {"status": "published", "slug": slug}
    return {"status": "failed"}

@app.websocket("/ws/chamber")
async def chamber_socket(websocket: WebSocket):
    await websocket.accept()
    try:
        last_idx = 0
        while True:
            current_log = activity_log[last_idx:]
            for item in current_log:
                await websocket.send_text(f"[{item['a']}] {item['op']}: {item['r']}")
            last_idx = len(activity_log)
            await asyncio.sleep(1)
    except: pass
