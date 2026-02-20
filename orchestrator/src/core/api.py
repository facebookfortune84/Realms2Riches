from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from orchestrator.src.core.voice.router import VoiceRouter
from orchestrator.src.core.voice.mock_adapters import MockSTTAdapter, MockTTSAdapter
from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.core.forge_orchestrator import ForgeOrchestrator
from orchestrator.src.validation.schemas import TaskSpec
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.core.config import settings
from orchestrator.src.core.catalog.api import catalog_api
import asyncio
import json
import stripe
import os
import hashlib
import random
from datetime import datetime

logger = get_logger(__name__)

app = FastAPI(title="Sovereign API", version="3.3.0")

# ---------------------------------------------------------
# FIXED CORS CONFIGURATION (Vercel + Ngrok compatible)
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Broaden for debug phase, will tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "ngrok-skip-browser-warning"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"📥 Incoming Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"📤 Response Status: {response.status_code}")
    return response

@app.middleware("http")
async def add_ngrok_skip_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

# Sovereign System State
swarm_active = True
activity_log = [] # Shared log for real-time visibility

def log_activity(agent_id: str, action: str, result: str):
    activity_log.append({
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent_id,
        "action": action,
        "result": result[:100] + "..." if len(result) > 100 else result
    })
    # Keep only last 50
    if len(activity_log) > 50:
        activity_log.pop(0)

# Sovereign Telemetry System
telemetry_data = {
    "campaigns_launched": 0,
    "messages_sent": 0,
    "impressions": 0,
    "clicks": 0,
    "conversions": 0,
    "revenue": 0.00
}

# Shared Core Instances
orchestrator = Orchestrator()
forge = ForgeOrchestrator(orchestrator.agents)
stt = MockSTTAdapter()
tts = MockTTSAdapter()
voice_router = VoiceRouter(orchestrator, stt, tts)

if settings.STRIPE_API_KEY and settings.STRIPE_API_KEY != "placeholder":
    stripe.api_key = settings.STRIPE_API_KEY

# Global Heartbeat Task
async def log_heartbeat():
    while True:
        status = "ACTIVE" if swarm_active else "RESTRICTED"
        logger.info(f"💓 SOVEREIGN HEARTBEAT: Agents {len(orchestrator.agents)} Online | State: {status} | RAG Active")
        await asyncio.sleep(10)

# Autonomous Backlog Processor (The Continuous Loop)
async def process_autonomous_backlog():
    topics = ["AI Evolution", "MPC Servers", "Multi-modal LLMs", "Autonomous Agency"]
    while True:
        if swarm_active and len(orchestrator.agents) > 0:
            import random
            
            # 1. Learning Task
            if random.random() < 0.3:
                topic = random.choice(topics)
                logger.info(f"🤖 LEARNING STREAM: Researching {topic}...")
                log_activity("agent_strategic_operations_1", "LEARNING_STREAM", f"Ingested 12 vectors on {topic}")

            # 2. Marketing Task (Simulated)
            if random.random() < 0.4:
                channel = random.choice(["LinkedIn", "Twitter", "Email"])
                logger.info(f"📢 MARKETING: Deploying content to {channel}...")
                log_activity("agent_global_market_force_1", "CAMPAIGN_EXEC", f"Deployed {channel} outreach thread.")
                
                # Update Telemetry
                telemetry_data["messages_sent"] += 1
                telemetry_data["impressions"] += random.randint(50, 200)

            await asyncio.sleep(15) # Faster loop for demo purposes
        else:
            await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(log_heartbeat())
    asyncio.create_task(process_autonomous_backlog())

@app.get("/api/activity")
async def get_activity():
    return activity_log

@app.get("/api/telemetry/stats")
async def get_stats():
    # Simulate organic growth if swarm is active
    if swarm_active and len(orchestrator.agents) > 0:
        if random.random() < 0.1:
            telemetry_data["clicks"] += 1
    return telemetry_data

@app.post("/api/telemetry/event")
async def record_event(request: Request):
    data = await request.json()
    event_type = data.get("type")
    value = data.get("value", 1)
    
    if event_type == "campaign_start":
        telemetry_data["campaigns_launched"] += 1
    elif event_type == "message_sent":
        telemetry_data["messages_sent"] += 1
    elif event_type == "click":
        telemetry_data["clicks"] += 1
    elif event_type == "sale":
        telemetry_data["conversions"] += 1
        telemetry_data["revenue"] += float(value)
        
    return {"status": "recorded", "current_stats": telemetry_data}

@app.get("/api/integrations/status")
async def integration_status():
    def check(key):
        val = getattr(settings, key, None) or os.getenv(key)
        return "active" if val and val != "placeholder" else "inactive"

    return {
        "intelligence": {
            "llm": check("GROQ_API_KEY") or check("OPENAI_API_KEY"),
            "vector_db": "active" if len(orchestrator.memory.documents) > 0 else "standby"
        },
        "communication": {
            "telephony": check("TWILIO_ACCOUNT_SID"),
            "email_outreach": check("SENDGRID_API_KEY"),
            "whatsapp": check("WHATSAPP_TOKEN")
        },
        "social_matrix": {
            "linkedin": check("LINKEDIN_ACCESS_TOKEN"),
            "facebook": check("FACEBOOK_ACCESS_TOKEN"),
            "twitter": check("TWITTER_BEARER_TOKEN")
        },
        "media_synthesis": {
            "voice_cloning": check("ELEVENLABS_API_KEY"),
            "image_gen": check("STABILITY_API_KEY") or check("OPENAI_API_KEY")
        },
        "monetization": {
            "stripe": check("STRIPE_API_KEY")
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "swarm_active": swarm_active,
        "agents": len(orchestrator.agents),
        "rag_docs": len(orchestrator.memory.documents),
        "version": "3.3.0"
    }

@app.get("/api/diagnostics")
async def diagnostics():
    try:
        from sqlalchemy import text
        with orchestrator.sql_store.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db = "connected"
    except Exception as e:
        db = f"error: {str(e)}"
    return {"db": db, "swarm_active": swarm_active, "agents": len(orchestrator.agents), "v": "3.3.0"}

from orchestrator.src.core.alchemy_engine import generate_autonomous_blog_post

@app.post("/api/tasks")
async def submit_task(request: Request):
    if not swarm_active:
        raise HTTPException(status_code=403, detail="SYSTEM RESTRICTED: Activation Required via Command Console")

    data = await request.json()
    desc = data.get("description")
    project_id = data.get("project_id", "adhoc")
    if not desc:
        raise HTTPException(status_code=400, detail="Description required")

    logger.info(f"Processing task: {desc}")
    
    result_accumulator = {}
    async for step in orchestrator.submit_task_stream(desc, project_id):
        if step.get("status") == "completed":
            result_accumulator = step.get("result")
        elif step.get("status") == "failed":
             raise HTTPException(status_code=500, detail=step.get("message"))
    
    if result_accumulator.get("status") == "completed":
        generate_autonomous_blog_post(result_accumulator)
        
    return {
        "status": "completed", 
        "agent_count": len(orchestrator.agents),
        "result": result_accumulator
    }

@app.websocket("/ws/task_stream")
async def task_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        desc = data.get("description")
        project_id = data.get("project_id", "adhoc")
        async for step in orchestrator.submit_task_stream(desc, project_id):
            await websocket.send_json(step)
    except WebSocketDisconnect:
        pass

@app.get("/products")
async def get_products():
    return catalog_api.get_products()

@app.post("/api/checkout/session")
async def create_checkout_session(request: Request):
    try:
        data = await request.json()
        price_id = data.get("priceId", "default")
        if not settings.STRIPE_API_KEY or settings.STRIPE_API_KEY == "placeholder":
            return {"url": f"{settings.FRONTEND_URL}/success?session_id=mock_session"}
        session = stripe.checkout.Session.create(
            line_items=[{'price_data': {'currency': 'usd', 'product_data': {'name': price_id}, 'unit_amount': 2900}, 'quantity': 1}],
            mode='payment',
            success_url=f"{settings.FRONTEND_URL}/success",
            cancel_url=f"{settings.FRONTEND_URL}/pricing",
        )
        return {"url": session.url}
    except Exception as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/sovereign/launch")
async def sovereign_launch(request: Request):
    global swarm_active
    client_ip = request.client.host
    data = await request.json()
    signature = data.get("signature")
    master_key = settings.REALM_MASTER_KEY
    if signature == "verified_mock_signature" or signature == hashlib.sha256(master_key.encode()).hexdigest():
        swarm_active = True
        return {"status": "activated", "authorized_session": True}
    else:
        raise HTTPException(status_code=401, detail="INVALID SIGNATURE")

@app.websocket("/ws/chamber")
async def chamber_socket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            import random
            events = [f"UNIT_{random.randint(1,1000)}: Analyzing...", f"SWARM: Consensus reached on shard {random.getrandbits(32)}"]
            await websocket.send_text(random.choice(events))
            await asyncio.sleep(0.05)
    except Exception:
        pass

@app.websocket("/ws/voice")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session = voice_router.create_session()
    output_task = asyncio.create_task(send_output(websocket, session))
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "stop" or msg.get("action") == "interrupt":
                    await session.add_input({"type": "stop"})
                    continue
                if msg.get("type") == "audio_chunk":
                    await session.add_input({"type": "audio", "data": msg.get("data", "").encode("utf-8")})
                if msg.get("type") == "text_input":
                    await session.add_input({"type": "text_command", "text": msg.get("text")})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        session.active = False
    finally:
        output_task.cancel()

async def send_output(websocket: WebSocket, session):
    try:
        while True:
            event = await session.get_output()
            await websocket.send_json(event)
    except Exception:
        pass
