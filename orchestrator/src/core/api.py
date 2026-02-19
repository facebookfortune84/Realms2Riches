from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from orchestrator.src.core.voice.router import VoiceRouter
from orchestrator.src.core.voice.mock_adapters import MockSTTAdapter, MockTTSAdapter
from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.core.config import settings
from orchestrator.src.core.catalog.api import catalog_api
import asyncio
import json
import stripe

logger = get_logger(__name__)

app = FastAPI()

# CORS
origins = [
    settings.FRONTEND_URL,
    "http://localhost:5173", # Local dev
    "https://frontend-two-xi-gal9lkptfi.vercel.app" # Current Vercel
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev simplicity, tighten in strict prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In a real app, use dependency injection or a lifespan manager
orchestrator = Orchestrator()
stt = MockSTTAdapter()
tts = MockTTSAdapter()
voice_router = VoiceRouter(orchestrator, stt, tts)

if settings.STRIPE_API_KEY and settings.STRIPE_API_KEY != "placeholder":
    stripe.api_key = settings.STRIPE_API_KEY

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/products")
async def get_products():
    return catalog_api.get_products()

import os
import glob

# ... (existing imports)

from orchestrator.src.core.forge_orchestrator import ForgeOrchestrator
from orchestrator.src.validation.schemas import TaskSpec

# ... (existing imports)

# Initialize Forge Orchestrator with the agents from the main Orchestrator
# Note: orchestrator.agents is populated in orchestrator.__init__
forge = ForgeOrchestrator(orchestrator.agents)

@app.get("/api/integrity")
async def get_system_integrity():
    manifest_path = "data/lineage/integrity_manifest.json"
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            return json.load(f)
    return {"status": "error", "message": "Manifest not found"}

@app.get("/metrics")
async def get_metrics():
    # Placeholder for real metrics aggregation
    # In a real system, this would query DB or memory store
    return {
        "tasks_processed_total": 42, # Mock
        "tasks_failed_total": 0,
        "orders_total": 5,
        "voice_sessions_total": 12,
        "blog_posts_count": 2,
        "agents_online": len(forge.list_agents())
    }

@app.get("/api/agents")
async def list_agents():
    return forge.list_agents()

@app.get("/api/agents/health")
async def health_check_agents():
    return forge.health_check_agents()

@app.post("/api/tasks")
async def submit_task(request: Request):
    data = await request.json()
    description = data.get("description")
    if not description:
        raise HTTPException(status_code=400, detail="Description required")
        
    task_spec = TaskSpec(
        project_id="adhoc", # Default for cockpit tasks
        description=description
    )
    result = forge.route_task(task_spec)
    return result

@app.get("/api/blog/posts")
async def list_blog_posts():
    manifest_path = "data/blog/posts.json"
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    posts = []
    blog_dir = "data/blog"
    if not os.path.exists(blog_dir):
        return []
        
    for filepath in glob.glob(os.path.join(blog_dir, "*.md")):
        slug = os.path.basename(filepath).replace(".md", "")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            # Simple frontmatter parse
            if content.startswith("---"):
                _, fm, _ = content.split("---", 2)
                lines = fm.strip().split("\n")
                meta = {"slug": slug}
                for line in lines:
                    if ":" in line:
                        key, val = line.split(":", 1)
                        meta[key.strip()] = val.strip().strip('"')
                posts.append(meta)
    return posts

@app.get("/api/blog/posts/{slug}")
async def get_blog_post(slug: str):
    filepath = os.path.join("data/blog", f"{slug}.md")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Post not found")
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        # Separate frontmatter and body
        if content.startswith("---"):
            _, fm, body = content.split("---", 2)
            lines = fm.strip().split("\n")
            meta = {"slug": slug}
            for line in lines:
                if ":" in line:
                    key, val = line.split(":", 1)
                    meta[key.strip()] = val.strip().strip('"')
            return {"meta": meta, "content": body.strip()}
            
    return {"meta": {"slug": slug}, "content": content}

@app.post("/api/checkout/session")
async def create_checkout_session(request: Request):
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
        
    data = await request.json()
    price_id = data.get("priceId") # Expecting a predefined price ID or we map it
    # For demo, we create a price or use a dummy one if not in DB map
    # Real impl: look up price_id in DB to get Stripe Price ID
    
    try:
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Titan Forge Plan'},
                    'unit_amount': 2900, # Placeholder
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{settings.FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/pricing",
        )
        return {"url": session.url}
    except Exception as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/checkout/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
        
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        logger.info(f"Payment successful: {session['id']}")
        
    return {"status": "success"}

@app.websocket("/ws/voice")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session = voice_router.create_session()
    
    # Send initial session info
    await websocket.send_json({"type": "session_start", "session_id": session.session_id})

    # Start a background task to push events from session -> client
    output_task = asyncio.create_task(send_output(websocket, session))
    
    try:
        while True:
            # Simple text-based JSON protocol for this demo
            data = await websocket.receive_text()
            
            try:
                msg = json.loads(data)
                msg_type = msg.get("type")
                
                if msg_type == "audio_chunk":
                    # Simulate audio arrival. In real app, this might be binary.
                    # Here we take "data" string and encode it to bytes to mimic audio
                    audio_content = msg.get("data", "").encode("utf-8")
                    await session.add_input({"type": "audio", "data": audio_content})
                elif msg_type == "stop":
                    await session.add_input({"type": "stop"})
                    break
                elif msg_type == "control":
                    # E.g. forced barge-in signal from client
                    action = msg.get("action")
                    if action == "interrupt":
                        # Manually trigger interruption logic
                        # But session logic handles barge-in on audio arrival too
                        pass

            except json.JSONDecodeError:
                logger.warning("Invalid JSON received")
                
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {session.session_id}")
    finally:
        output_task.cancel()
        if session.session_id in voice_router.sessions:
            del voice_router.sessions[session.session_id]

async def send_output(websocket: WebSocket, session):
    try:
        while True:
            event = await session.output_queue.get()
            if event:
                await websocket.send_json(event)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Error sending output: {e}")
