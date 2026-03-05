import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.validation.schemas import ToolInvocation
from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class SMTPOutreachTool(BaseTool):
    """
    High-Density SMTP Outreach Tool for Stream 12.
    Uses standard SMTP for maximum compatibility across autonomous nodes.
    """
    def execute(self, invocation: ToolInvocation) -> Dict[str, Any]:
        params = invocation.input_data
        target_email = params.get("target_email")
        target_name = params.get("target_name", "Entrepreneur")
        subject = params.get("subject", f"Strategic Intelligence for {target_name}")
        html_body = params.get("html_body")
        
        if not target_email or "@" not in str(target_email):
            return {"status": "error", "reason": "Invalid target email"}
            
        if not html_body:
            return {"status": "error", "reason": "Missing HTML body for outreach"}

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"Robert DeMotto <{settings.SMTP_USER}>"
            msg["To"] = target_email

            part = MIMEText(html_body, "html")
            msg.attach(part)

            logger.info(f"📧 DISPATCHING SMTP OUTREACH TO {target_email} via {settings.SMTP_SERVER}")
            
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
                server.sendmail(settings.SMTP_USER, target_email, msg.as_string())
            
            return {
                "status": "success",
                "target": target_email,
                "method": "smtp",
                "server": settings.SMTP_SERVER
            }
        except Exception as e:
            logger.error(f"❌ SMTP DISPATCH FAILED: {e}")
            return {"status": "error", "reason": str(e)}

def get_smtp_tools() -> List[BaseTool]:
    cfg = {
        "type": "object",
        "properties": {
            "target_email": {"type": "string"},
            "target_name": {"type": "string"},
            "subject": {"type": "string"},
            "html_body": {"type": "string"}
        },
        "required": ["target_email", "html_body"]
    }
    return [
        SMTPOutreachTool(ToolConfig(
            tool_id="smtp_outreach",
            name="SMTP Outreach",
            description="High-density SMTP dispatch for cold outreach swarms",
            parameters_schema=cfg,
            allowed_agents=["*"]
        ))
    ]
