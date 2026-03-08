from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
import logging
import time
import os
import json
from collections import defaultdict

# Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TRAFFIC_MANAGER")

app = FastAPI()

# Simple In-Memory Click Store (Persistence could be added later)
CLICK_DATA_FILE = "data/customers/clicks.json"
os.makedirs("data/customers", exist_ok=True)

class TrafficManager:
    def __init__(self):
        self.clicks = defaultdict(int)
        self.load_clicks()

    def load_clicks(self):
        if os.path.exists(CLICK_DATA_FILE):
            try:
                with open(CLICK_DATA_FILE, "r") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        self.clicks[k] = v
            except Exception as e:
                logger.error(f"Failed to load clicks: {e}")

    def save_clicks(self):
        try:
            with open(CLICK_DATA_FILE, "w") as f:
                json.dump(self.clicks, f)
        except Exception as e:
            logger.error(f"Failed to save clicks: {e}")

    def record_click(self, source: str, campaign: str):
        key = f"{source}_{campaign}"
        self.clicks[key] += 1
        self.save_clicks()
        logger.info(f"🖱️ CLICK RECORDED: {source} -> {campaign} | Total: {self.clicks[key]}")

traffic_manager = TrafficManager()

@app.get("/r")
async def redirect_link(target: str, source: str = "unknown", campaign: str = "general"):
    """
    Redirects traffic to the target URL and logs the click.
    Usage: http://localhost:8000/r?target=https://stripe.com...&source=tiktok&campaign=viral_v1
    """
    traffic_manager.record_click(source, campaign)
    return RedirectResponse(url=target)

@app.get("/stats")
async def get_stats():
    """Returns click statistics for the orchestrator to consume."""
    return JSONResponse(content=traffic_manager.clicks)

@app.get("/")
async def root():
    return {"status": "Traffic Manager Online", "clicks_recorded": sum(traffic_manager.clicks.values())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
