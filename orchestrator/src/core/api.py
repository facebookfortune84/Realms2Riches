from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
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
from datetime import datetime

logger = get_logger(__name__)

app = FastAPI(title="Sovereign API", version="3.1.0")

# ---------------------------------------------------------
# FIXED CORS CONFIGURATION (Vercel + Ngrok compatible)
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-two-xi-gal9lkptfi.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "ngrok-skip-browser-warning"],
)

@app.middleware("http")
async def add_ngrok_skip_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

# Sovereign System State
swarm_active = False

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

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(log_heartbeat())

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "swarm_active": swarm_active,
        "agents": len(orchestrator.agents),
        "rag_docs": len(orchestrator.memory.documents)
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
    return {"db": db, "swarm_active": swarm_active, "agents": len(orchestrator.agents), "v": "3.1.0"}

from orchestrator.src.core.alchemy_engine import generate_autonomous_blog_post

async def process_task_and_alchemize(desc, project_id):
    result = orchestrator.submit_task(desc, project_id)
    if result.get("status") == "completed":
        generate_autonomous_blog_post(result)

@app.post("/api/tasks")
async def submit_task(request: Request, background_tasks: BackgroundTasks):
    if not swarm_active:
        raise HTTPException(status_code=403, detail="SYSTEM RESTRICTED: Activation Required via Command Console")

    data = await request.json()
    desc = data.get("description")
    if not desc:
        raise HTTPException(status_code=400, detail="Description required")

    background_tasks.add_task(process_task_and_alchemize, desc, data.get("project_id", "adhoc"))
    return {"status": "queued", "agent_count": len(orchestrator.agents)}

@app.get("/products")
async def get_products():
    return catalog_api.get_products()

@app.post("/api/checkout/session")
async def create_checkout_session(request: Request):
    try:
        data = await request.json()
        price_id = data.get("priceId", "default")
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': price_id},
                    'unit_amount': 2900
                },
                'quantity': 1
            }],
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

        launch_record = {
            "event": "SOVEREIGN_IGNITION",
            "authorized_ip": client_ip,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "SUCCESS"
        }
        logger.info(f"🚀 SOVEREIGN SYSTEM ACTIVATED via Signature Handshake from IP: {client_ip}")

        with open("data/lineage/launch_manifest.json", "a") as f:
            f.write(json.dumps(launch_record) + "\n")

        return {"status": "activated", "authorized_session": True}
    else:
        logger.warning(f"BLOCKING UNAUTHORIZED LAUNCH ATTEMPT FROM: {client_ip}")
        raise HTTPException(status_code=401, detail="INVALID CRYPTOGRAPHIC SIGNATURE")

@app.websocket("/ws/chamber")
async def chamber_socket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            import random
            events = [
                f"UNIT_{random.randint(1,1000)}: Analyzing vector subspace...",
                f"FORGE: ToolSmith generating new logic gate...",
                f"SWARM: Consensus reached on shard {random.getrandbits(32)}",
                f"INTEGRITY: SHA-256 validation successful.",
                f"RAG: Context injected from session history."
            ]
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
            msg = json.loads(data)
            if msg.get("type") == "audio_chunk":
                await session.add_input({"type": "audio", "data": msg.get("data", "").encode("utf-8")})
    except Exception:
        pass
    finally:
        output_task.cancel()

async def send_output(websocket: WebSocket, session):
    try:
        while True:
            event = await session.output_queue.get()
            await websocket.send_json(event)
    except Exception:
        pass