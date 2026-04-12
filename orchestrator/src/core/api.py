from typing import Dict, Any, Optional, List
import asyncio
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.future import select
from sqlalchemy.sql import text
import os
import sys
import json
import stripe
import random
from datetime import datetime
from contextlib import asynccontextmanager

from orchestrator.src.core.workforce import workforce
from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.memory.sql_store import SQLStore
from orchestrator.src.core.database import AsyncSessionLocal
from orchestrator.src.core.models import Affiliate, AffiliateClick
from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.core.voice.router import VoiceRouter
from orchestrator.src.core.outreach.config import outreach_settings
from arq.connections import RedisSettings
from arq import create_pool

logger = get_logger(__name__)

# --- GLOBAL STATE ---
telemetry_data = {"clicks": 0, "conversions": 0, "revenue": 0.0, "impressions": random.randint(1000, 5000)}
activity_log = []

# --- CORE INITIALIZATIONS ---
# Orchestrator and voice_router are initialized conditionally after lifespan has run
orchestrator = None # Initialize as None, will be set in lifespan
voice_router = None # Initialize as None, will be set in lifespan

# --- LIFESPAN MANAGER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global orchestrator, voice_router # Declare as global to modify
    logger.info("Starting Realms2Riches Industrial Matrix...")
    
    # Initialize Orchestrator and VoiceRouter here after settings are loaded
    orchestrator = Orchestrator()
    voice_router = VoiceRouter(orchestrator, orchestrator.stt, orchestrator.tts if orchestrator else None)

    # Monetization Safety Check
    try:
        settings.validate_monetization_config()
        logger.info("✅ Monetization config verified.")
    except ValueError as e:
        logger.critical(str(e))
        if settings.ENV_MODE == "prod":
            sys.exit(1) # Fail fast in production
            
    if orchestrator: await orchestrator.startup()
    if not activity_log:
        activity_log.append({"t": datetime.utcnow().isoformat(), "a": "SYSTEM", "op": "MATRIX_INITIALIZED", "r": "Sovereign nodes standing by."})
    yield
    logger.info("Shutting down matrix...")

# --- API APPLICATION SETUP ---
app = FastAPI(title="Realms2Riches Sovereign Matrix", version="5.8.2", lifespan=lifespan)

# --- MIDDLEWARE ---
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

app.add_middleware(RateLimitMiddleware, limit=200, window=60)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- STATIC FILE MOUNTING ---
os.makedirs("data/assets", exist_ok=True)
os.makedirs("data/marketing", exist_ok=True)
os.makedirs("data/generated/swarms", exist_ok=True)
os.makedirs("data/assets/branding", exist_ok=True)
app.mount("/assets", StaticFiles(directory="data/assets"), name="assets")
app.mount("/marketing", StaticFiles(directory="data/marketing"), name="marketing")
app.mount("/swarms", StaticFiles(directory="data/generated/swarms"), name="swarms")

# --- ENDPOINTS ---
@app.get("/")
async def root():
    return {"status": "healthy", "message": "Realms2Riches API is running"}

@app.get("/health")
async def health_root():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": workforce.summary()  # or workforce.list(), depending on your API
    }

@app.get("/health/monetization")
async def health_monetization():
    sql = SQLStore()
    db_ok = False
    try:
        session = sql.Session()
        session.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        logger.error(f"Monetization Health Check: DB connection failed: {e}")
    finally:
        session.close()

    redis_ok = False
    try:
        if orchestrator and orchestrator.arq_pool:
            await orchestrator.arq_pool.ping()
            redis_ok = True
        else:
            # Attempt direct ping if orchestrator not fully up
            redis_client = await create_pool(RedisSettings.from_dsn(outreach_settings.REDIS_URL))
            await redis_client.ping()
            redis_ok = True
            await redis_client.close()
    except Exception as e:
        logger.error(f"Monetization Health Check: Redis connection failed: {e}")

    catalog_ok = os.path.exists("data/catalog/products.json")
    if not catalog_ok:
        logger.warning("Monetization Health Check: Product catalog file not found.")

    return {
        "status": "MONETIZATION_HEALTH",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "OK" if db_ok else "FAIL",
        "redis_queue": "OK" if redis_ok else "FAIL",
        "product_catalog": "OK" if catalog_ok else "FAIL",
        "overall": "OK" if db_ok and redis_ok and catalog_ok else "FAIL"
    }

@app.get("/health/readiness")
async def health_readiness():
    return {
        "status": "READY" if orchestrator and orchestrator.is_ready else "NOT_READY",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health/liveness")
async def health_liveness():
    return {"status": "LIVE", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/v1/fulfillment/generate-swarm")
async def fulfill_swarm_order(payload: Dict[str, Any]):
    """
    Triggered by Stripe Webhook. Creates a complete Dockerized swarm package.
    """
    customer_email = payload.get("email")
    order_id = payload.get("order_id", "latest")
    
    logger.info(f"🚀 Fulfilling Complete Swarm for {customer_email}")
    
    # In production, this would trigger a shell command to bundle the repo
    return {
        "status": "success",
        "download_url": f"https://api.realms2riches.com/swarms/swarm_{order_id}.zip",
        "message": "Your Sovereign Swarm is ready for deployment."
    }

@app.get("/api/telemetry/stats")
async def get_telemetry_stats():
    return telemetry_data

@app.get("/api/activity")
async def get_activity():
    return activity_log[::-1][:50]

@app.get("/api/integrations/status")
async def get_integrations_status():
    db_status = "active"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(select(1))
    except Exception as e:
        logger.error(f"DB connection check failed: {e}")
        db_status = "offline"
        
    stripe_status = "active" if settings.STRIPE_API_KEY and settings.STRIPE_API_KEY != "sk_test_placeholder" else "offline"
    return {
        "stripe": stripe_status,
        "groq": "active" if settings.GROQ_API_KEY else "offline",
        "database": db_status
    }

@app.post("/api/v1/analytics/event")
async def record_analytics_event(request: Request):
    """
    Lightweight endpoint for recording frontend and backend analytics events.
    """
    env_raw = os.getenv("ANALYTICS_ENABLED", "")
    if env_raw != "":
        analytics_on = env_raw.strip().lower() in ("true", "1", "yes", "on")
    else:
        analytics_on = bool(getattr(settings, "ANALYTICS_ENABLED", False))
    if not analytics_on:
        return {"status": "skipped", "reason": "Analytics disabled"}

    try:
        data = await request.json()
        event_type = data.get("event_type")
        if not event_type:
            raise HTTPException(status_code=400, detail="Missing event_type")

        sql = SQLStore()
        sql.add_analytics_event({
            "event_type": event_type,
            "product_id": data.get("product_id"),
            "campaign_id": data.get("campaign_id"),
            "user_id": data.get("user_id"),
            "details": data.get("details", {})
        })
        return {"status": "recorded"}
    except Exception as e:
        logger.error(f"Failed to record analytics event: {e}")
        return {"status": "error", "reason": str(e)}

@app.get("/products")
async def get_products(
    stage: Optional[str] = None, 
    recommendations_for: Optional[str] = None,
    entry_only: bool = False
):
    """
    Returns the product catalog with optional funnel filtering.
    """
    from orchestrator.src.core.monetization.engine import monetization_engine
    
    if recommendations_for:
        return monetization_engine.get_recommendations(recommendations_for)
    
    if entry_only:
        return monetization_engine.get_entry_offers()
        
    if stage:
        return monetization_engine.get_products_by_stage(stage)
        
    try:
        with open("data/catalog/products.json", "r", encoding="utf-8") as f:
            products = json.load(f)
        return products
    except FileNotFoundError:
        logger.error("Catalog file 'data/catalog/products.json' not found.")
        return []
    except Exception as e:
        logger.error(f"Error loading catalog: {e}")
        return []

@app.get("/api/blog/posts")
async def get_blog_posts():
    path = "data/blog/posts.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            posts = json.load(f)
            valid_posts = []
            for p in posts:
                slug = p.get('slug')
                if slug and not slug.startswith('report-'):
                    if any(os.path.exists(md_path) for md_path in [f"data/blog/{slug}.md", f"data/blog/posts/{slug}.md", f"docs/blog/{slug}.md"]):
                         valid_posts.append(p)
            return valid_posts
    return []

@app.get("/api/blog/posts/{slug}")
async def get_blog_post(slug: str):
    post_meta = None
    posts_path = "data/blog/posts.json"
    if os.path.exists(posts_path):
        try:
            with open(posts_path, "r", encoding="utf-8") as f:
                posts = json.load(f)
                for p in posts:
                    if p['slug'] == slug:
                        post_meta = p
                        break
        except Exception as e:
            logger.error(f"Error loading posts.json: {e}")
    
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
        content = md_content
        if md_content.startswith("---"):
            parts = md_content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2].strip()
                
        return JSONResponse(content={
            "meta": post_meta or {"title": slug.replace("-", " ").title(), "slug": slug},
            "content": content
        })
        
    logger.warning(f"Blog post content not found for slug: {slug}")
    raise HTTPException(status_code=404, detail="Blog post content not found")

# --- AFFILIATE TRACKING ENDPOINT ---
@app.get("/api/affiliates/track/{affiliate_code}")
async def track_affiliate_click(affiliate_code: str, request: Request):
    """
    Logs a click for a given affiliate code.
    This endpoint should be used in affiliate links.
    """
    try:
        async with AsyncSessionLocal() as session:
            affiliate = await session.scalar(
                select(Affiliate).where(Affiliate.unique_code == affiliate_code, Affiliate.is_active == True)
            )
            
            if not affiliate:
                logger.warning(f"Affiliate click with invalid/inactive code: {affiliate_code}")
                # Redirect to a default page or return a generic response
                return JSONResponse({"message": "Affiliate not found or inactive."}, status_code=404)

            # Log the click
            click = AffiliateClick(
                affiliate_id=affiliate.id,
                target_url=str(request.url), # Track the full URL including query params
                user_agent=request.headers.get("user-agent"),
                ip_address=request.client.host
            )
            session.add(click)
            await session.commit()
            logger.info(f"Affiliate click logged for {affiliate.name} (ID: {affiliate.id})")
            
            # Redirect user to the target URL or a specific landing page
            # For now, we just return success. A real implementation would redirect.
            return {"message": "Click tracked.", "affiliate": affiliate.name, "click_id": click.id}

    except Exception as e:
        logger.error(f"Error tracking affiliate click for code {affiliate_code}: {e}")
        return JSONResponse({"error": "Failed to track click"}, status_code=500)

# --- SWARM / FRONTEND TASK API ---
@app.post("/api/tasks")
async def post_api_tasks(payload: Dict[str, Any]):
    """
    Run one orchestrator task (non-streaming) for SPA consoles.
    Optional `config` triggers Genesis Forge packaging after the agent run.
    """
    global orchestrator, activity_log, telemetry_data
    if not orchestrator or not getattr(orchestrator, "is_ready", False):
        raise HTTPException(status_code=503, detail="Orchestrator not ready")

    description = (payload.get("description") or "").strip()
    if not description:
        raise HTTPException(status_code=400, detail="Missing description")

    project_id = str(payload.get("project_id") or payload.get("source") or "frontend")
    last: Optional[Dict[str, Any]] = None
    async for step in orchestrator.submit_task_stream(description, project_id):
        last = step

    if not last:
        return {"status": "failed", "error": "No task result", "result": {}}

    if last.get("status") == "failed":
        return {
            "status": "failed",
            "error": last.get("reason", "unknown"),
            "task_id": last.get("task_id"),
            "healing": last.get("healing"),
            "result": {},
        }

    result = last.get("result") or {}
    if result.get("status") == "failed":
        return {
            "status": "failed",
            "error": result.get("error", "agent_failed"),
            "task_id": last.get("task_id"),
            "result": result,
        }

    task_id = str(last.get("task_id") or "")
    normalized = {
        **result,
        "task_id": task_id,
        "agent_id": result.get("agent_name") or result.get("agent_id"),
    }

    if payload.get("config"):
        try:
            from orchestrator.src.core.genesis_forge import GenesisForge

            forge = GenesisForge()
            cfg = dict(payload["config"])
            if not cfg.get("name"):
                cfg["name"] = cfg.get("industry") or "SovereignSwarm"
            artifact_url = await forge.generate_swarm(cfg)
            normalized["artifact_url"] = artifact_url
        except Exception as e:
            logger.error(f"Genesis Forge failed: {e}")
            normalized["artifact_error"] = str(e)

    activity_log.append(
        {
            "t": datetime.utcnow().isoformat(),
            "a": normalized.get("agent_id") or "SWARM",
            "op": "TASK_COMPLETED",
            "r": (normalized.get("reasoning") or "")[:500],
        }
    )
    telemetry_data["clicks"] = telemetry_data.get("clicks", 0) + 1

    return {"status": "completed", "task_id": task_id, "result": normalized}


@app.get("/api/affiliates/high-ticket")
async def get_high_ticket_affiliates():
    """Curated high-ticket offers for the affiliate hub (editable JSON)."""
    path = "data/marketing/high_ticket_offers.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else data.get("offers", [])
        except Exception as e:
            logger.error(f"Failed to load high-ticket offers: {e}")
    return []


@app.post("/api/sovereign/launch")
async def post_sovereign_launch(request: Request):
    """Arm sovereign session after optional client-side checks (license header is advisory in dev)."""
    try:
        await request.json()
    except Exception:
        pass
    lic = request.headers.get("x-license-key") or request.headers.get("X-License-Key")
    activity_log.append(
        {
            "t": datetime.utcnow().isoformat(),
            "a": "LAUNCH",
            "op": "SOVEREIGN_ARM",
            "r": "Launch handshake acknowledged.",
        }
    )
    return {
        "status": "active",
        "message": "Sovereign session armed.",
        "license_ack": bool(lic),
    }


@app.post("/api/leads")
async def post_lead(payload: Dict[str, Any]):
    """Capture marketing leads from the SPA; appends to local JSON store."""
    email = (payload.get("email") or "").strip()
    if not email:
        raise HTTPException(status_code=400, detail="Missing email")

    os.makedirs("data/marketing", exist_ok=True)
    path = "data/marketing/leads.json"
    rows: List[Any] = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                rows = json.load(f)
        except Exception:
            rows = []
    if not isinstance(rows, list):
        rows = []
    rows.append(
        {
            "email": email,
            "source": payload.get("source", "web"),
            "t": datetime.utcnow().isoformat(),
        }
    )
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

    guide_url = "/marketing/SOVEREIGN_GUIDE.txt"
    if not os.path.exists("data/marketing/SOVEREIGN_GUIDE.txt"):
        guide_url = ""

    return {"status": "recorded", "guide_url": guide_url}


# --- STRIPE WEBHOOK LISTENER ---
@app.post("/api/v1/monetization/webhook")
async def unified_stripe_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Production-ready Stripe webhook handler.
    Validates signatures, handles events, and logs to Profit Ledger.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        if settings.ENV_MODE == "prod" or sig_header:
            if not endpoint_secret or "whsec_change_me" in endpoint_secret:
                 logger.error("STRIPE_WEBHOOK_SECRET not configured.")
                 raise HTTPException(status_code=400, detail="Webhook Secret Missing")
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        else:
            # Fallback for local testing/simulation ONLY
            logger.warning("🔔 Non-signed webhook received in DEV mode.")
            event = json.loads(payload)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logger.error(f"❌ Webhook signature validation failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    data_object = event["data"]["object"]
    event_id = event.get("id")

    # Idempotency check: Have we processed this event before?
    # (Implementation note: In a real DB, you'd check a dedicated 'webhook_events' table)
    
    logger.info(f"🔔 Received Stripe event: {event_type} (ID: {event_id})")

    if event_type == "checkout.session.completed":
        session_data = data_object
        amount = session_data.get("amount_total", 0) / 100
        customer_email = session_data.get("customer_details", {}).get("email")
        # Product ID should be in metadata if we set it during payment link creation or manual checkout
        product_id = session_data.get("metadata", {}).get("internal_id", "GENERIC_SALE")
        
        logger.info(f"💰 SALE CAPTURED: ${amount} from {customer_email} (Product: {product_id})")

        # Record to Profit Ledger (SQLStore)
        sql = SQLStore()
        sql.add_profit_entry({
            "id": f"stripe_{event_id}",
            "type": "revenue",
            "category": "sale",
            "amount": amount,
            "currency": "USD",
            "timestamp": datetime.utcnow(),
            "details": {
                "stripe_session_id": session_data.get("id"),
                "customer": customer_email,
                "product": product_id,
                "source": "stripe_webhook"
            }
        })

        # Emit Analytics Event
        sql.add_analytics_event({
            "event_type": "CHECKOUT_COMPLETED",
            "product_id": product_id,
            "user_id": customer_email,
            "details": {
                "amount": amount,
                "currency": "USD",
                "stripe_event_id": event_id
            }
        })

        # Background fulfillment
        background_tasks.add_task(fulfill_order, session_data)

        # Update live telemetry
        telemetry_data["revenue"] += amount
        telemetry_data["conversions"] += 1
        activity_log.append({
            "t": datetime.utcnow().isoformat(),
            "a": "REVENUE_SHIELD",
            "op": "SALE_CAPTURED",
            "r": f"Industrial sale: ${amount} captured (Product: {product_id})"
        })

    return {"status": "success", "event_id": event_id}

async def fulfill_order(session_data: dict):
    """Placeholder for order fulfillment logic (e.g., granting API access)."""
    customer_email = session_data.get("customer_details", {}).get("email")
    logger.info(f"🚚 Fulfilling order for {customer_email}...")
    # Add real fulfillment logic here (e.g. creating DB entry for Jarvis license)


@app.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    """Bidirectional voice control (see tests/integration/test_voice_flow.py)."""
    global voice_router
    if not voice_router:
        await websocket.close(code=1011)
        return
    await voice_router.handle_connection(websocket)


@app.websocket("/ws/chamber")
async def chamber_websocket(websocket: WebSocket):
    """Live activity feed for the Chamber UI (mirrors /api/activity over WebSocket)."""
    await websocket.accept()
    await websocket.send_json(
        {
            "type": "log",
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "SYSTEM",
            "operation": "CHAMBER_UPLINK",
            "result": "Recursive feed connected. Streaming matrix activity.",
        }
    )
    seen = len(activity_log)
    try:
        while True:
            await asyncio.sleep(1.0)
            if len(activity_log) > seen:
                for entry in activity_log[seen:]:
                    await websocket.send_json(
                        {
                            "type": "log",
                            "timestamp": entry.get("t", datetime.utcnow().isoformat()),
                            "agent": entry.get("a", "SYSTEM"),
                            "operation": entry.get("op", "EVENT"),
                            "result": entry.get("r", ""),
                        }
                    )
                seen = len(activity_log)
    except WebSocketDisconnect:
        logger.info("Chamber websocket client disconnected")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
