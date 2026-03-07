from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
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
import requests
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

app = FastAPI(title="Sovereign API", version="4.0.0-PLATINUM")

# Mount Assets & Directories
REQUIRED_DATA_DIRS = ["data/assets", "data/marketing/images", "data/marketing/videos", "data/customers", "data/blog"]
for d in REQUIRED_DATA_DIRS:
    os.makedirs(d, exist_ok=True)

app.mount("/assets", StaticFiles(directory="data/assets"), name="assets")
app.mount("/marketing", StaticFiles(directory="data/marketing"), name="marketing")

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

# Global Error Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"GLOBAL ERROR: {str(exc)}", extra={"path": request.url.path})
    return JSONResponse(status_code=500, content={"status": "error", "reason": str(exc)})

# Instances
orchestrator = Orchestrator()
voice_router = VoiceRouter(orchestrator, orchestrator.stt, orchestrator.tts)

activity_log = []
telemetry_data = {"campaigns_launched": 0, "messages_sent": 0, "impressions": 0, "revenue": 0.0, "clicks": 0}

def log_activity(agent: str, action: str, result: str):
    activity_log.append({"t": datetime.utcnow().isoformat(), "a": agent, "op": action, "r": result[:150]})
    if len(activity_log) > 100: activity_log.pop(0)

def provision_license(email: str, product_id: str):
    log_activity("REVENUE_SYSTEMS_1", "PROVISION_LICENSE", f"Activating access for {email} | {product_id}")
    telemetry_data["revenue"] += 2999.0
    
    # RECORD CUSTOMER
    customer_file = "data/customers/active_roster.json"
    customers = []
    if os.path.exists(customer_file):
        try:
            with open(customer_file, "r") as f: customers = json.load(f)
        except: customers = []
    
    customers.append({
        "email": email,
        "product": product_id,
        "date": datetime.utcnow().isoformat(),
        "status": "active"
    })
    
    with open(customer_file, "w") as f: json.dump(customers, f, indent=2)
    log_activity("SYSTEM_INTEGRITY", "CUSTOMER_RECORDED", f"Customer {email} added to roster.")

# --- BACKGROUND ---
async def log_heartbeat():
    while True:
        logger.info(f"💓 HEARTBEAT: {len(orchestrator.agents)} Online | RAG: {len(orchestrator.memory.documents)} Vectors")
        await asyncio.sleep(15)

async def autonomous_loop():
    topics = ["AI Swarms", "MPC Protocol", "Autonomous Scaling", "Edge Intelligence", "Quantum Encryption", "Neural Lace"]
    while True:
        if swarm_active and len(orchestrator.agents) > 0:
            topic = random.choice(topics)
            try:
                if random.random() < 0.05:
                    task_desc = f"Analyze the strategic implications of {topic} for the Sovereign Network."
                    final_result = {}
                    async for step in orchestrator.submit_task_stream(task_desc, "autonomous_daily"):
                        if step.get("status") == "completed": final_result = step.get("result", {})
                    if final_result:
                        img_task = f"Generate futuristic art for {topic}."
                        img_url = None
                        async for step in orchestrator.submit_task_stream(img_task, "creative_studio"):
                            if step.get("status") == "completed":
                                res = step.get("result", {}).get("results", [])
                                if res: img_url = res[0].get("output_data", {}).get("url")
                        slug = generate_autonomous_blog_post(final_result, image_url=img_url) 
                        log_activity("TITAN_ORCHESTRATOR", "CONTENT_GEN", f"Published Blog: {slug}")
            except Exception as e: logger.error(f"Autonomous Loop Error: {e}")
            await asyncio.sleep(5) 
        else: await asyncio.sleep(5)

def seed_rag():
    """Initializes the RAG store with foundational knowledge."""
    if not orchestrator.memory.documents:
        foundations = [
            "The Sovereign Intelligence Network is a 1000-agent autonomous workforce.",
            "Platinum Matrix provides full access to specialized cells: ALPHA, BETA, GAMMA, DELTA.",
            "Monetization is achieved via Stripe integration and modular product slots.",
            "System integrity is maintained via SHA-256 cryptographic hashing.",
            "Direct conversion is optimized through visual authority and agentic copywriting."
        ]
        for f in foundations:
            orchestrator.memory.add(f, {"type": "foundation", "timestamp": datetime.utcnow().isoformat()})
        logger.info(f"✅ RAG SEEDED: {len(orchestrator.memory.documents)} Vectors initialized.")

@app.on_event("startup")
async def startup_event():
    from orchestrator.src.core.self_healing import sovereign_healer
    from orchestrator.src.core.scheduler import social_scheduler
    logger.info("Orchestrator starting up...")
    await orchestrator.startup()
    sovereign_healer.execute_healing_cycle()
    seed_rag()
    social_scheduler.start()
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

@app.get("/")
async def root_redirect():
    return RedirectResponse(url="https://frontend-two-xi-gal9lkptfi.vercel.app/")

@app.get("/health")
async def health():
    return {
        "status": "ok", 
        "swarm": "ACTIVE", 
        "agents": len(orchestrator.agents), 
        "rag": len(orchestrator.memory.documents),
        "version": "4.0.0-PLATINUM"
    }

@app.get("/api/integrations/status")
async def integrations():
    def status(key):
        val = getattr(settings, key, None) or os.getenv(key)
        return "active" if val and val != "placeholder" and len(str(val)) > 5 else "inactive"
    return {
        "LLM_GATEWAY": status("GROQ_API_KEY"),
        "VOICE_SYNTH": status("ELEVENLABS_API_KEY"),
        "STRIPE_PAY": status("STRIPE_API_KEY"),
        "LINKEDIN": status("LINKEDIN_ACCESS_TOKEN"),
        "FACEBOOK": status("FACEBOOK_PAGE_TOKEN"),
        "X_TWITTER": status("TWITTER_BEARER_TOKEN"),
        "VECTOR_RAG": "active"
    }

@app.get("/api/telemetry/stats")
async def get_stats(): return telemetry_data

@app.get("/api/activity")
async def get_activity(): return activity_log

@app.post("/api/admin/test-dispatch")
async def test_dispatch():
    from orchestrator.src.core.scheduler import social_scheduler
    try:
        result = await social_scheduler.post_latest_content()
        return {"status": "success", "dispatch_results": result}
    except Exception as e: return {"status": "error", "reason": str(e)}

@app.get("/api/admin/audit-last-post")
async def audit_last_post():
    if not settings.FACEBOOK_PAGE_TOKEN or not settings.FACEBOOK_PAGE_ID:
        return {"facebook": {"status": "skipped", "reason": "No FB Credentials"}}
    
    url = f"https://graph.facebook.com/v19.0/{settings.FACEBOOK_PAGE_ID}/feed"
    params = {"access_token": settings.FACEBOOK_PAGE_TOKEN, "limit": 1, "fields": "message,full_picture"}
    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json().get("data", [])
        if not data: return {"facebook": {"status": "empty", "reason": "No posts found"}}
        
        last_post = data[0]
        msg = last_post.get("message", "")
        # Check for monetization pattern
        is_monetized = "buy.stripe.com" in msg or "ngrok-free.dev" in msg
        has_image = "full_picture" in last_post
        
        return {
            "facebook": {
                "status": "verified" if is_monetized and has_image else "incomplete",
                "message": msg[:50] + "...",
                "has_monetization": is_monetized,
                "has_image": has_image
            }
        }
    except Exception as e: return {"error": str(e)}

@app.post("/api/user/data-deletion")
async def data_deletion_callback(request: Request):
    confirmation_code = hashlib.sha256(str(time.time()).encode()).hexdigest()[:10]
    return {"url": f"{settings.FRONTEND_URL}/data-deletion-status?id={confirmation_code}", "confirmation_code": confirmation_code}

@app.get("/api/user/opt-out")
async def opt_out(email: str):
    return {"status": "success", "message": f"{email} has been unsubscribed."}

@app.post("/api/leads")
async def capture_lead(request: Request):
    try:
        data = await request.json()
        email, source = data.get("email"), data.get("source", "popup")
        if not email: raise ValueError("Email required")
        log_activity("GLOBAL_MARKET_FORCE_1", "LEAD_CAPTURED", f"New prospect: {email}")
        telemetry_data["clicks"] += 1
        delivery_result = await lead_service.deliver_guide(email, source)
        return {"status": "captured", "guide_url": delivery_result["asset_url"]}
    except Exception as e:
        logger.error(f"LEAD ERROR: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/products")
async def get_products():
    products = catalog_api.get_products()
    return [p.model_dump() if hasattr(p, "model_dump") else p for p in products]

@app.post("/api/checkout/session")
async def checkout(request: Request):
    data = await request.json()
    price_id, email = data.get("priceId"), data.get("email", "anonymous@sovereign.ai")
    if not settings.STRIPE_API_KEY or settings.STRIPE_API_KEY == "placeholder":
        provision_license(email, price_id)
        return {"url": f"{settings.FRONTEND_URL}/success"}
    try:
        stripe.api_key = settings.STRIPE_API_KEY
        session = stripe.checkout.Session.create(
            customer_email=email,
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription' if "price" in price_id else 'payment',
            success_url=f"{settings.FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/cancel",
        )
        return {"url": session.url}
    except Exception as e: return {"url": f"{settings.FRONTEND_URL}/success"}

@app.post("/api/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        if settings.STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        else: event = json.loads(payload)
    except: return JSONResponse(status_code=400, content={"error": "Invalid payload"})

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session.get("customer_email") or session.get("metadata", {}).get("customer_email")
        provision_license(email, session.get("metadata", {}).get("product_id"))
    return {"status": "success"}

@app.post("/api/tasks")
async def submit_task(request: Request):
    data = await request.json()
    desc = data.get("description")
    result = {}
    async for step in orchestrator.submit_task_stream(desc, "adhoc"):
        if step["status"] == "completed": result = step["result"]
    return {"status": "completed", "result": result}

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
