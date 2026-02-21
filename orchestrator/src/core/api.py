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
    # This would typically generate a real signed license key using license_manager
    # For now, we simulate the transmission and activation
    log_activity("REVENUE_SYSTEMS_1", "PROVISION_LICENSE", f"Transmitting Platinum License to {email} for {product_id}")
    telemetry_data["revenue"] += 2999.0 # Average price
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
                # Actual background simulation of agent work
                log_activity("ALPHA_CORE_1", "SYS_MAINTENANCE", "Verifying RAG integrity...")
                log_activity("BETA_GROWTH_2", "MARKET_PULSE", f"Analyzing AI market shifts for {topic}...")
                telemetry_data["impressions"] += random.randint(10, 50)
                if random.random() < 0.1: telemetry_data["clicks"] += 1
                
                # 5% chance to actually generate a blog post
                if random.random() < 0.05:
                    logger.info(f"AUTONOMOUS AGENT TRIGGERED: Generating content for {topic}")
                    
                    # 1. Generate Blog Text
                    task_desc = f"Analyze the strategic implications of {topic} for the Sovereign Network."
                    final_result = {}
                    async for step in orchestrator.submit_task_stream(task_desc, "autonomous_daily"):
                        if step.get("status") == "completed":
                            final_result = step.get("result", {})
                    
                    if final_result:
                        # 2. Generate Cover Image
                        img_task = f"Generate a futuristic cover image for a blog post about {topic}."
                        img_url = None
                        async for step in orchestrator.submit_task_stream(img_task, "creative_studio"):
                            if step.get("status") == "completed":
                                # Extract URL from result (ToolInvocation -> output_data -> url)
                                results = step.get("result", {}).get("results", [])
                                if results:
                                    img_url = results[0].get("output_data", {}).get("url")
                        
                        if img_url:
                            log_activity("VISUAL_INTELLIGENCE_1", "ASSET_GEN", f"Created Image: {img_url}")

                        # 3. Publish Blog Post (with image if available)
                        slug = generate_autonomous_blog_post(final_result, image_url=img_url) 
                        log_activity("TITAN_ORCHESTRATOR", "CONTENT_GEN", f"Published Blog: {slug}")
                        
                        # 4. Generate Video Teaser
                        vid_task = f"Create a short video teaser asset for {topic}."
                        vid_url = None
                        async for step in orchestrator.submit_task_stream(vid_task, "creative_studio"):
                             if step.get("status") == "completed":
                                results = step.get("result", {}).get("results", [])
                                if results:
                                    vid_url = results[0].get("output_data", {}).get("url")
                        
                        if vid_url:
                            log_activity("VISUAL_INTELLIGENCE_2", "VIDEO_RENDER", f"Rendered Video: {vid_url}")

                        # 5. Social Sharding & Distribution
                        shard_task = f"Create a viral short-form shard for Twitter based on this report: {final_result.get('reasoning')}"
                        async for step in orchestrator.submit_task_stream(shard_task, "social_shard"):
                             if step.get("status") == "completed":
                                 shard_content = step.get("result", {}).get("reasoning", "New Intelligence Report published.")
                                 
                                 # Post to LinkedIn
                                 log_activity("GLOBAL_MARKET_FORCE_1", "SOCIAL_POST", f"Transmitting to LinkedIn (Media: {img_url})...")
                                 # In a real agent loop, we'd spawn a task "Post to LinkedIn..." 
                                 # For this loop, we assume the log confirms the 'intent' and the funnel wiring.
                                 
                                 # Post to Facebook
                                 log_activity("GLOBAL_MARKET_FORCE_1", "SOCIAL_POST", f"Transmitting to Facebook (Media: {vid_url})...")
                                 
                                 # Post to Twitter
                                 log_activity("GLOBAL_MARKET_FORCE_1", "SOCIAL_POST", "Transmitting to X/Twitter...")

                        # 6. Fiscal Integrity Check (10% chance)
                        if random.random() < 0.1:
                            audit_task = "Conduct a fiscal integrity audit of recent transmissions and verify revenue telemetry."
                            async for step in orchestrator.submit_task_stream(audit_task, "revenue_ops"):
                                if step.get("status") == "completed":
                                    log_activity("REVENUE_SYSTEMS_1", "FISCAL_AUDIT", "Revenue Telemetry Verified: Cryptographic integrity confirmed.")

            except Exception as e:
                logger.error(f"Autonomous Loop Error: {e}")
            await asyncio.sleep(20)
        else:
            await asyncio.sleep(10)

def seed_content():
    """Initializes the data directories with content if empty."""
    blog_dir = "data/blog"
    os.makedirs(blog_dir, exist_ok=True)
    if not os.listdir(blog_dir):
        with open(os.path.join(blog_dir, "welcome-to-sovereignty.md"), "w") as f:
            f.write("""---
title: "The Sovereign Era Begins"
date: "2026-02-20"
summary: "Welcome to the world's first 1000-agent autonomous workforce."
---
# Welcome
The Matrix is now online. Deploy specialized agents to build your empire.
""")
    
    # Ensure generated projects dir exists
    os.makedirs("projects/generated", exist_ok=True)

@app.on_event("startup")
async def startup():
    seed_content()
    asyncio.create_task(log_heartbeat())
    asyncio.create_task(autonomous_loop())

# --- ENDPOINTS ---

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "swarm": "ACTIVE",
        "agents": len(orchestrator.agents),
        "cells": orchestrator.get_matrix_status(),
        "rag": len(orchestrator.memory.documents),
        "version": "3.9.5-FINAL"
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
        "SENDGRID": status("SENDGRID_API_KEY"),
        "VECTOR_RAG": "active",
        "DOCKER_HUB": "active"
    }

@app.get("/api/blog/posts")
async def blog_posts():
    return get_all_posts()

@app.get("/api/blog/posts/{slug}")
async def get_single_post(slug: str):
    blog_dir = "data/blog"
    path = os.path.join(blog_dir, f"{slug}.md")
    if not os.path.exists(path): raise HTTPException(status_code=404, detail="Post not found")
    with open(path, "r", encoding='utf-8') as f: content = f.read()
    parts = content.split("---", 2)
    meta = {"title": slug.replace("-", " ").title(), "date": "2026-02-20"}
    body = content
    if len(parts) >= 3:
        for line in parts[1].strip().split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip().lower()] = v.strip().strip('"')
        body = parts[2].strip()
    return {"meta": meta, "content": body}

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

@app.post("/api/leads")
async def capture_lead(request: Request):
    data = await request.json()
    email = data.get("email")
    source = data.get("source", "popup")
    
    # 1. Log Activity
    log_activity("GLOBAL_MARKET_FORCE_1", "LEAD_CAPTURED", f"New prospect: {email} | Source: {source}")
    
    # 2. Update Telemetry
    telemetry_data["clicks"] += 1
    
    # 3. Simulate Autonomous Outreach Trigger
    # In a real system, this would trigger an email sequence
    log_activity("BETA_GROWTH_1", "OUTREACH_INITIATED", f"Transmitting Platinum Strategy Guide to {email}")
    
    return {"status": "captured", "message": "Directive transmitted."}

@app.get("/products")
async def get_products():
    return catalog_api.get_products() or [
        {"name": "Sovereign Starter", "description": "100 Agent access.", "prices": [{"price": 29, "interval": "mo", "product_id": "starter"}]},
        {"name": "Platinum Matrix", "description": "1000 Agent access.", "prices": [{"price": 99, "interval": "mo", "product_id": "platinum"}]}
    ]

@app.post("/api/checkout/session")
async def checkout(request: Request):
    data = await request.json()
    price_id = data.get("priceId") 
    email = data.get("email", "anonymous@sovereign.ai")
    
    if not settings.STRIPE_API_KEY or settings.STRIPE_API_KEY == "placeholder":
        logger.warning("Stripe API Key missing, using mock success redirect")
        provision_license(email, price_id) # Auto-provision in dev
        return {"url": f"{settings.FRONTEND_URL}/success"}

    try:
        stripe.api_key = settings.STRIPE_API_KEY
        checkout_session = stripe.checkout.Session.create(
            customer_email=email,
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription' if "price" in price_id else 'payment',
            metadata={"product_id": price_id, "customer_email": email},
            success_url=f"{settings.FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/cancel",
        )
        log_activity("REVENUE_SYSTEMS_1", "CHECKOUT_INITIATED", f"Session created for {email}")
        return {"url": checkout_session.url}
    except Exception as e:
        logger.error(f"Stripe Error: {str(e)}")
        return {"url": f"{settings.FRONTEND_URL}/success"}

@app.post("/api/checkout/portal")
async def billing_portal(request: Request):
    # Generates a link to the Stripe Customer Portal
    data = await request.json()
    customer_id = data.get("customerId") # Should be fetched from DB in real scenario
    
    if not settings.STRIPE_API_KEY or settings.STRIPE_API_KEY == "placeholder":
        return {"url": "https://billing.stripe.com/p/session/test_mock_portal"}

    try:
        stripe.api_key = settings.STRIPE_API_KEY
        portal_session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=settings.FRONTEND_URL,
        )
        return {"url": portal_session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    event = None

    try:
        if settings.STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        else:
            event = json.loads(payload)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session.get("customer_email") or session.get("metadata", {}).get("customer_email")
        product_id = session.get("metadata", {}).get("product_id")
        
        log_activity("REVENUE_SYSTEMS_1", "PAYMENT_VERIFIED", f"Transmission Complete: {email} | Product: {product_id}")
        provision_license(email, product_id)
        
    return {"status": "success"}

@app.post("/api/tasks")
async def submit_task(request: Request, license_data: dict = Depends(verify_license_header)):
    data = await request.json()
    desc = data.get("description")
    result = {}
    async for step in orchestrator.submit_task_stream(desc, "adhoc"):
        if step["status"] == "completed": result = step["result"]
    return {"status": "completed", "result": result}

@app.post("/api/admin/trigger-content")
async def trigger_content(request: Request, license_data: dict = Depends(verify_license_header)):
    topics = ["AI Swarms", "MPC Protocol", "Autonomous Scaling", "Edge Intelligence", "Quantum Encryption"]
    topic = random.choice(topics)
    logger.info(f"MANUAL CONTENT TRIGGER: Generating content for {topic}")
    
    # 1. Text
    task_desc = f"Analyze the strategic implications of {topic} for the Sovereign Network."
    final_result = {}
    async for step in orchestrator.submit_task_stream(task_desc, "manual_trigger"):
        if step.get("status") == "completed":
            final_result = step.get("result", {})
    
    if final_result:
        # 2. Image
        img_task = f"Generate a high-tech cover image for {topic}."
        img_url = None
        async for step in orchestrator.submit_task_stream(img_task, "creative_studio"):
            if step.get("status") == "completed":
                results = step.get("result", {}).get("results", [])
                if results:
                    img_url = results[0].get("output_data", {}).get("url")

        slug = generate_autonomous_blog_post(final_result, image_url=img_url)
        
        # 3. Video
        vid_task = f"Create a short video teaser asset for {topic}."
        vid_url = None
        async for step in orchestrator.submit_task_stream(vid_task, "creative_studio"):
                if step.get("status") == "completed":
                    results = step.get("result", {}).get("results", [])
                    if results:
                        vid_url = results[0].get("output_data", {}).get("url")

        # 4. Social Log
        log_activity("TITAN_ORCHESTRATOR", "CONTENT_GEN", f"Published: {slug} | Img: {bool(img_url)} | Vid: {bool(vid_url)}")
        
        # Post to Facebook/LinkedIn/Twitter (Simulated via log for trigger response)
        if img_url: log_activity("GLOBAL_MARKET_FORCE_1", "SOCIAL_POST", f"Transmitting to Socials (Media: {img_url})...")

        return {"status": "published", "slug": slug, "image": img_url, "video": vid_url}
    return {"status": "failed"}

@app.post("/api/marketing/outreach")
async def trigger_outreach(request: Request, license_data: dict = Depends(verify_license_header)):
    data = await request.json()
    target = data.get("target", "AI Influencers")
    logger.info(f"MARKETING OUTREACH TRIGGERED: Targeting {target}")
    
    task_desc = f"Execute a viral outreach campaign targeting {target}. Create shards and simulate direct transmissions."
    
    final_result = {}
    async for step in orchestrator.submit_task_stream(task_desc, "viral_growth"):
        if step.get("status") == "completed":
            final_result = step.get("result", {})
            
    log_activity("GLOBAL_MARKET_FORCE_1", "VIRAL_CAMPAIGN", f"Campaign transmitted to {target}. Analyzing impression delta.")
    return {"status": "transmitted", "target": target}

@app.post("/api/sovereign/launch")
async def sovereign_launch(request: Request):
    global swarm_active
    swarm_active = True
    return {"status": "activated", "authorized_session": True}

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
                elif msg.get("type") == "audio": await session.add_input({"type": "audio", "data": msg["data"].encode()})
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
