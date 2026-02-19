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

logger = get_logger(__name__)

app = FastAPI(title="Sovereign API", version="3.1.0")

# Robust CORS for Ngrok and Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared Core Instances
orchestrator = Orchestrator()
forge = ForgeOrchestrator(orchestrator.agents)
stt = MockSTTAdapter()
tts = MockTTSAdapter()
voice_router = VoiceRouter(orchestrator, stt, tts)

if settings.STRIPE_API_KEY and settings.STRIPE_API_KEY != "placeholder":
    stripe.api_key = settings.STRIPE_API_KEY

@app.get("/health")
async def health():
    return {
        "status": "ok", 
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
    return {"db": db, "agents": len(orchestrator.agents), "v": "3.1.0"}

from orchestrator.src.core.alchemy_engine import generate_autonomous_blog_post

# ... (inside submit_task)
async def process_task_and_alchemize(desc, project_id):
    result = orchestrator.submit_task(desc, project_id)
    if result.get("status") == "completed":
        generate_autonomous_blog_post(result)

@app.post("/api/tasks")
async def submit_task(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    desc = data.get("description")
    if not desc:
        raise HTTPException(status_code=400, detail="Description required")
    
    # Decouple submission and trigger alchemy upon success
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
            line_items=[{'price_data': {'currency': 'usd', 'product_data': {'name': price_id}, 'unit_amount': 2900}, 'quantity': 1}],
            mode='payment',
            success_url=f"{settings.FRONTEND_URL}/success",
            cancel_url=f"{settings.FRONTEND_URL}/pricing",
        )
        return {"url": session.url}
    except Exception as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

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
    except Exception: pass
    finally: output_task.cancel()

async def send_output(websocket: WebSocket, session):
    try:
        while True:
            event = await session.output_queue.get()
            await websocket.send_json(event)
    except Exception: pass
