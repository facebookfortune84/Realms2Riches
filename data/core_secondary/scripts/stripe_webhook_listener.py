from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from starlette.responses import JSONResponse, HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.future import select
import os
import json
import csv
import stripe
import random
from datetime import datetime
from contextlib import asynccontextmanager

from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.core.database import AsyncSessionLocal # Ensure Base is imported correctly
from orchestrator.src.core.models import Affiliate, AffiliateClick # Import new models
from orchestrator.src.core.orchestrator import Orchestrator

logger = get_logger(__name__)

# --- GLOBAL STATE ---
telemetry_data = {"clicks": 0, "conversions": 0, "revenue": 0.0, "impressions": random.randint(1000, 5000)}
activity_log = []

# --- CORE INITIALIZATIONS ---
orchestrator = Orchestrator() if 'orchestrator' in locals() and orchestrator else Orchestrator()
voice_router = VoiceRouter(orchestrator, orchestrator.stt, orchestrator.tts if orchestrator else None) if orchestrator else None

# --- API APPLICATION SETUP ---
app = FastAPI(title="Realms2Riches Sovereign Matrix", version="5.8.2", lifespan=lifespan)

# --- LIFESPAN MANAGER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Realms2Riches Industrial Matrix...")
    if orchestrator: await orchestrator.startup()
    if not activity_log:
        activity_log.append({"t": datetime.utcnow().isoformat(), "a": "SYSTEM", "op": "MATRIX_INITIALIZED", "r": "Sovereign nodes standing by."})
    yield
    logger.info("Shutting down matrix...")

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

@app.get("/health")
async def health_check():
    return {"status": "SOVEREIGN", "timestamp": datetime.utcnow().isoformat(), "agents_online": len(orchestrator.agents) if orchestrator else 0}

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

@app.get("/products")
async def get_products():
    products = []
    try:
        with open("data/catalog/products.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            product_map = {row['id']: row for row in reader}
        
        with open("data/catalog/prices.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                p_id = row['product_id']
                if p_id in product_map:
                    p = product_map[p_id].copy()
                    p['price'] = float(row['price'])
                    p['currency'] = row['currency']
                    p['interval'] = row['interval']
                    if p.get('image_url') and not p['image_url'].startswith('http'):
                        p['image_url'] = p['image_url'] # Assume it's relative to /assets
                    products.append(p)
        return products
    except FileNotFoundError:
        logger.error("Catalog files not found.")
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

# --- STRIPE WEBHOOK LISTENER ---
@app.post("/api/v1/monetization/webhook")
async def unified_stripe_webhook(request: Request, background_tasks: BackgroundTasks):
    internal_header = request.headers.get("x-sovereign-internal")
    is_internal = (internal_header == "true")
    payload = await request.body()
    
    if is_internal:
        event = json.loads(payload)
    else:
        sig_header = request.headers.get("stripe-signature")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        try:
            if endpoint_secret:
                event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            else:
                # Fallback for local testing without secret
                event = json.loads(payload)
        except ValueError as e:
            logger.error(f"Webhook error: Invalid payload - {e}")
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            raise HTTPException(status_code=400, detail="Invalid signature")
        except Exception as e:
            logger.error(f"An unexpected error occurred during webhook event construction: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during event construction")

    event_type = event["type"]
    data_object = event["data"]["object"]

    logger.info(f"🔔 Received Stripe event: {event_type}")

    if event_type == "checkout.session.completed":
        session_data = data_object
        amount = session_data.get("amount_total", 0) / 100
        customer_email = session_data.get("customer_details", {}).get("email")
        product_id = session_data.get("metadata", {}).get("product_id", "GENERIC_SALE")
        session_id = session_data.get("id")
        affiliate_code = session_data.get("metadata", {}).get("affiliate_code") # Extract affiliate code from metadata
        
        logger.info(f"Checkout session completed for {customer_email}, Product ID: {product_id}, Amount: ${amount}")

        # Fulfill the purchase using background tasks
        background_tasks.add_task(fulfill_order, session_data)

        # Update telemetry
        telemetry_data["revenue"] += amount
        telemetry_data["conversions"] += 1
        activity_log.append({
            "t": datetime.utcnow().isoformat(),
            "a": "REVENUE_SHIELD",
            "op": "SALE_CAPTURED",
            "r": f"Industrial sale: ${amount} captured from {customer_email} (Product: {product_id})"
        })
    
    elif event_type == "payment_intent.succeeded":
        payment_intent = data_object
        logger.info(f"PaymentIntent succeeded: {payment_intent['id']}")
        # Potentially handle payment intents directly if needed, or assume checkout.session.completed covers it
        
    elif event_type == "customer.subscription.created":
        subscription = data_object
        logger.info(f"Subscription created: {subscription['id']}")
        # Handle subscription events (e.g., grant access, log to DB)

    elif event_type == "invoice.payment_succeeded":
        invoice = data_object
        logger.info(f"Invoice paid: {invoice['id']}")
        # Handle invoice payment success (e.g., for recurring payments)

    else:
        logger.warning(f"Unhandled Stripe event type: {event_type}")

    return {"status": "success"}

async def fulfill_order(session_data: dict):
    """
    Background task to fulfill the order.
    """
    logger.info(f"📦 FULFILLING ORDER: {session_data.get('id')}")
    # In a real scenario, this would:
    # 1. Grant access to the product
    # 2. Send a confirmation email
    # 3. Update the database
    customer_email = session_data.get("customer_details", {}).get("email")
    product_id = session_data.get("metadata", {}).get("product_id")
    
    logger.info(f"✅ Access granted to {product_id} for {customer_email}")

@app.get("/api/v1/user/jarvis")
async def get_jarvis_iframe():
    """Serves the industrial AI orchestration interface."""
    return HTMLResponse(content="<html><body style='background:black;color:white;'><h1>JARVIS_v3.5_CORE</h1><p>Neural Uplink Active.</p></body></html>")

if __name__ == "__main__":
    import uvicorn
    # Note: Running this file directly might not reflect the full FastAPI app setup with middleware, etc.
    # It's primarily for direct testing or running the webhook listener in isolation.
    # Use the main SOVEREIGN_START.ps1 script for the full application launch.
    uvicorn.run(app, host="0.0.0.0", port=8000) # Changed port to 8000 to match API default, was 4242
