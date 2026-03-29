import logging
from mcp.server.fastmcp import FastMCP
from orchestrator.src.tools.smtp_tools import SMTPOutreachTool
from orchestrator.src.tools.base import ToolConfig

import sys
# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("mcp-outreach")

# Initialize FastMCP Server
mcp = FastMCP("Realms2Riches Outreach Server")

def _get_tool(cls, name):
    return cls(ToolConfig(
        tool_id=name.lower(),
        name=name,
        description=f"MCP Wrapper for {name}",
        parameters_schema={},
        allowed_agents=["*"]
    ))

@mcp.tool()
async def send_email(target_email: str, html_body: str, subject: str = "Strategic Intelligence", target_name: str = "Entrepreneur") -> str:
    """Send a cold outreach email via SMTP."""
    tool = _get_tool(SMTPOutreachTool, "SMTPOutreach")
    result = tool.execute({
        "target_email": target_email, 
        "html_body": html_body, 
        "subject": subject, 
        "target_name": target_name
    })
    return str(result)

if __name__ == "__main__":
    mcp.run()
