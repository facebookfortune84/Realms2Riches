import sys
import os
import logging
from typing import Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger("UCP")
logging.basicConfig(level=logging.INFO)

class UnifiedControlPlane:
    """
    Unified Control Plane (UCP) for Realms2Riches.
    Manages connections to MCP servers and routes tool execution.
    """
    
    def __init__(self):
        # In a real containerized env, these might be HTTP/SSE URLs.
        # For this setup, we assume local subprocess execution (STDIO).
        self.server_registry = {
            "stripe": "mcp_internal.servers.stripe.server",
            "outreach": "mcp_internal.servers.outreach.server",
            "oracle": "mcp_internal.servers.oracle.server",
            "swarm": "mcp_internal.servers.swarm.server",
        }

    async def call(self, server: str, tool: str, args: Dict[str, Any] = {}) -> Any:
        """
        Executes a tool on a specific MCP server.
        """
        if server not in self.server_registry:
            raise ValueError(f"Unknown MCP server: {server}")

        module_path = self.server_registry[server]
        python_exe = sys.executable
        
        # Configure the server process
        server_params = StdioServerParameters(
            command=python_exe,
            args=["-m", module_path],
            env=os.environ.copy() # Inherit environment variables (API keys, etc.)
        )

        logger.info(f"UCP: Connecting to {server} ({module_path})...")

        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Verify tool exists
                    tools = await session.list_tools()
                    tool_names = [t.name for t in tools.tools]
                    if tool not in tool_names:
                        raise ValueError(f"Tool '{tool}' not found on {server}. Available: {tool_names}")
                    
                    logger.info(f"UCP: Invoking {server}.{tool}")
                    result = await session.call_tool(tool, args)
                    return result
        except Exception as e:
            logger.error(f"UCP Error calling {server}.{tool}: {e}")
            raise

    # Helper methods for common workflows
    async def create_checkout(self, email: str, product_id: str):
        return await self.call("stripe", "create_payment_link", {"email": email, "product_id": product_id})

    async def send_outreach(self, email: str, body: str, subject: str):
        return await self.call("outreach", "send_email", {"target_email": email, "html_body": body, "subject": subject})

    async def consult_oracle(self):
        return await self.call("oracle", "get_strategic_directives")

    async def dispatch_swarm(self, task: str):
        return await self.call("swarm", "dispatch_swarm_task", {"task_description": task})

# Singleton instance
ucp = UnifiedControlPlane()
