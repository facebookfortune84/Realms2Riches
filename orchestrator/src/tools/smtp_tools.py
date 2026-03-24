import smtplib
import logging
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from orchestrator.src.tools.base import BaseTool, ToolConfig
from orchestrator.src.validation.schemas import ToolInvocation
from orchestrator.src.core.config import settings
from orchestrator.src.core.outreach.config import outreach_settings
from orchestrator.src.memory.sql_store import SQLStore
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class SMTPOutreachTool(BaseTool):
    """
    High-Density SMTP Outreach Tool for Stream 12.
    Uses standard SMTP for maximum compatibility across autonomous nodes.
    """
    def execute(self, invocation: Any) -> Dict[str, Any]:
        params = invocation if isinstance(invocation, dict) else (invocation.input_data or {})
        target_email = params.get("target_email") or params.get("recipient")
        target_name = params.get("target_name", "Entrepreneur")
        subject = params.get("subject", f"Strategic Intelligence for {target_name}")
        html_body = params.get("html_body") or params.get("body")
        
        # 0. Global Safety Switch Check
        # Prioritize local outreach_settings for module-specific control
        if not outreach_settings.OUTREACH_ENABLED:
            logger.warning(f"🚫 OUTREACH DISABLED: Simulation only for {target_email}.")
            return {"status": "simulated", "reason": "OUTREACH_ENABLED is False", "target": target_email}

        if not target_email or not re.match(r"[^@]+@[^@]+\.[^@]+", str(target_email)):
            return {"status": "error", "reason": "Invalid or malformed target email"}
            
        if not html_body:
            return {"status": "error", "reason": "Missing HTML body for outreach"}

        # 1. Configuration Validation
        try:
            settings.validate_outreach_config()
        except ValueError as e:
            # If strictly required, fail. But if DRY RUN is on, we might proceed if the error is just missing creds but we are rerouting?
            # Actually, validate_outreach_config allows missing creds if DRY_RUN is True.
            logger.error(f"❌ OUTREACH CONFIG ERROR: {e}")
            return {"status": "error", "reason": str(e)}

        # 2. Dry Run / Test Mode Logic
        # Use outreach_settings.OUTREACH_DRY_RUN as the primary source of truth for this stream
        real_recipient = target_email
        if outreach_settings.OUTREACH_DRY_RUN:
            logger.info(f"🧪 DRY_RUN: Rerouting outreach from {target_email} to {outreach_settings.OUTREACH_TEST_RECIPIENT}")
            target_email = outreach_settings.OUTREACH_TEST_RECIPIENT

        # 3. Compliance: Ensure Unsubscribe Link exists
        if "unsubscribe" not in html_body.lower():
            unsubscribe_html = f'<p style="font-size: 10px; color: gray;">If you no longer wish to receive these communications, <a href="{settings.BACKEND_URL}/api/v1/outreach/unsubscribe?email={real_recipient}">click here to unsubscribe</a>.</p>'
            html_body += unsubscribe_html

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            # Use configured SMTP User as sender
            msg["From"] = f"{settings.BRAND_NAME} <{settings.SMTP_USER}>"
            msg["To"] = target_email

            part = MIMEText(html_body, "html")
            msg.attach(part)

            logger.info(f"📧 DISPATCHING SMTP OUTREACH TO {target_email} via {settings.SMTP_SERVER}:{settings.SMTP_PORT}")
            
            # Use SMTP_SSL for Port 465 (Gmail Preferred) or SMTP + STARTTLS for 587
            if settings.SMTP_PORT == 465:
                server = smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT)
            else:
                server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
                server.starttls()
                
            with server:
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
                server.sendmail(settings.SMTP_USER, target_email, msg.as_string())
            
            logger.info(f"✅ SMTP SUCCESS: {target_email}")

            # Emit Analytics Event
            try:
                sql = SQLStore()
                sql.add_analytics_event({
                    "event_type": "EMAIL_SENT",
                    "product_id": params.get("product_id"),
                    "campaign_id": params.get("campaign_id"),
                    "user_id": real_recipient, # Log the REAL intended recipient
                    "details": {"subject": subject, "method": "smtp", "actual_recipient": target_email}
                })
            except Exception as ae:
                logger.warning(f"Failed to emit analytics for email send: {ae}")

            return {
                "status": "success",
                "target": target_email,
                "original_target": real_recipient,
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
