import logging
import httpx
from mcp.server.fastmcp import FastMCP
from orchestrator.src.core.config import settings

import sys
# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("mcp-swarm")

# Initialize FastMCP Server
mcp = FastMCP("Realms2Riches Swarm Server")

API_BASE_URL = "https://api.realms2riches.com"

@mcp.tool()
async def dispatch_swarm_task(task_description: str) -> str:
    """Dispatch a task to the Sovereign Swarm."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{API_BASE_URL}/api/v1/swarm/dispatch",
                json={"task": task_description},
                timeout=10.0
            )
            resp.raise_for_status()
            return str(resp.json())
        except Exception as e:
            return f"Error dispatching task: {str(e)}"

@mcp.tool()
async def get_swarm_transparency() -> str:
    """Get real-time transparency metrics from the Swarm."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{API_BASE_URL}/api/v1/swarm/transparency", timeout=5.0)
            resp.raise_for_status()
            return str(resp.json())
        except Exception as e:
            return f"Error fetching transparency: {str(e)}"

@mcp.tool()
async def get_integrations_status() -> str:
    """Check status of external integrations."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{API_BASE_URL}/api/integrations/status", timeout=5.0)
            resp.raise_for_status()
            return str(resp.json())
        except Exception as e:
            return f"Error fetching status: {str(e)}"

if __name__ == "__main__":
    mcp.run()

