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
from orchestrator.src.core.licensing import license_manager
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.validation.schemas import TaskSpec
import asyncio
import json
import os
import time
import requests
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

logger = get_logger(__name__)

# Shared Core
orchestrator = Orchestrator()
boot_time = datetime.utcnow()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Async Boot
    await orchestrator.startup()
    
    # 2. Start Scheduled Tasks
    from orchestrator.src.core.self_healing import sovereign_healer
    from orchestrator.src.core.scheduler import social_scheduler
    sovereign_healer.execute_healing_cycle()
    social_scheduler.start()
    
    yield
    # Shutdown logic if needed

app = FastAPI(title="Sovereign API", version="5.0.0-PLATINUM", lifespan=lifespan)

# Rest of API logic...
voice_router = VoiceRouter(orchestrator, orchestrator.stt, orchestrator.tts)
activity_log = []
telemetry_data = {"campaigns_launched": 0, "messages_sent": 0, "impressions": 0, "revenue": 0.0, "clicks": 0}

def log_activity(agent: str, action: str, result: str):
    activity_log.append({"t": datetime.utcnow().isoformat(), "a": agent, "op": action, "r": result[:150]})
    if len(activity_log) > 100: activity_log.pop(0)

# --- MIDDLEWARE & MOUNTS ---
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/assets", StaticFiles(directory="data/assets"), name="assets")
app.mount("/marketing", StaticFiles(directory="data/marketing"), name="marketing")

@app.middleware("http")
async def skip_ngrok_warning(request: Request, call_next):
    response = await call_next(request)
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

# --- ENDPOINTS ---

@app.get("/")
async def root():
    return RedirectResponse(url="https://frontend-two-xi-gal9lkptfi.vercel.app/")

@app.get("/health")
async def health():
    if not orchestrator.is_ready:
        return {"status": "initializing", "message": "Matrix building in progress..."}
    return {
        "status": "ok", 
        "agents": len(orchestrator.agents), 
        "rag": len(orchestrator.memory.documents) if orchestrator.memory else 0,
        "uptime": str(datetime.utcnow() - boot_time)
    }

@app.get("/api/activity")
async def get_activity():
    return activity_log

@app.get("/api/workforce/role-call")
async def role_call():
    if not orchestrator.is_ready: raise HTTPException(status_code=503, detail="Not Ready")
    introductions = [
        f"Unit {a.dossier.tax_id} ({a.agent_name}) online as {a.active_persona['title'] if a.active_persona else 'BASE'}"
        for a in list(orchestrator.agents.values())[:10]
    ]
    return {"status": "synchronized", "roster": introductions}

@app.post("/api/admin/test-dispatch")
async def test_dispatch():
    from orchestrator.src.core.scheduler import social_scheduler
    result = await social_scheduler.post_latest_content()
    log_activity("SYSTEM_ADMIN", "TEST_DISPATCH", f"Results: {json.dumps(result)}")
    return {"status": "success", "dispatch_results": result}

@app.post("/api/leads")
async def capture_lead(request: Request):
    data = await request.json()
    log_activity("MARKET_FORCE", "LEAD_CAPTURED", f"Prospect: {data.get('email')}")
    return {"status": "captured", "guide_url": f"https://glowfly-sizeable-lazaro.ngrok-free.dev/assets/sovereign_strategy_guide_v3.txt"}

@app.get("/products")
async def get_products():
    return catalog_api.get_products()

@app.post("/api/tasks")
async def submit_task(request: Request):
    data = await request.json()
    result = {}
    async for step in orchestrator.submit_task_stream(data.get("description"), "adhoc"):
        if step["status"] == "completed": result = step["result"]
    return {"status": "completed", "result": result}
