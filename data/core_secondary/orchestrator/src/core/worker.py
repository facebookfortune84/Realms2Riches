from arq.connections import RedisSettings

# Ensure project root is in path for imports
import os
import sys
sys.path.append(os.getcwd())

from orchestrator.src.core.outreach.config import outreach_settings
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.tools.smtp_tools import SMTPOutreachTool
from orchestrator.src.memory.sql_store import SQLStore # For analytics events

logger = get_logger(__name__)

async def send_email_campaign_item(ctx, campaign_item: dict):
    """
    Background job to send a single email from a campaign.
    Handles logging, retries, and dry-run mode.
    """
    target_email = campaign_item.get("target_email")
    subject = campaign_item.get("subject")
    html_body = campaign_item.get("html_body")
    campaign_id = campaign_item.get("campaign_id", "default")
    product_id = campaign_item.get("product_id")
    
    if not target_email or not subject or not html_body:
        logger.error(f"Invalid campaign item received: {campaign_item}")
        return {"status": "failed", "reason": "Missing email components"}

    logger.info(f"Processing email for campaign '{campaign_id}' to {target_email} (Product: {product_id})")

    tool = SMTPOutreachTool()
    
    # Manually build invocation data
    invocation_data = {
        "target_email": target_email,
        "subject": subject,
        "html_body": html_body,
        "product_id": product_id,
        "campaign_id": campaign_id,
    }

    try:
        result = tool.execute(invocation_data) # SMTPOutreachTool handles dry_run and OUTREACH_ENABLED
        if result["status"] == "success":
            logger.info(f"✅ Campaign email successfully processed for {target_email} in campaign {campaign_id}")
        elif result["status"] == "simulated":
            logger.info(f"✅ Campaign email simulated for {target_email} in campaign {campaign_id} (Outreach Disabled)")
        else:
            logger.error(f"❌ Campaign email failed for {target_email}: {result.get('reason', 'unknown error')}")
        return result
    except Exception as e:
        logger.error(f"Unhandled exception during campaign email send to {target_email}: {e}")
        # Add event for failed email
        sql = SQLStore()
        sql.add_analytics_event({
            "event_type": "EMAIL_SEND_FAILED",
            "user_id": target_email,
            "campaign_id": campaign_id,
            "product_id": product_id,
            "details": {"reason": str(e)}
        })
        raise # Re-raise for arq retry mechanism

class WorkerSettings:
    functions = [send_email_campaign_item]
    redis_settings = RedisSettings.from_dsn(outreach_settings.REDIS_URL)
    job_timeout = 60 # seconds
    max_jobs = 10 # process up to 10 jobs concurrently
    keep_result = 3600 # keep results for 1 hour
    on_startup = [lambda ctx: logger.info("ARQ Worker started.")]
    on_shutdown = [lambda ctx: logger.info("ARQ Worker shutting down.")]

# This file itself is the worker definition.
# To run: arq worker orchestrator.src.core.worker.WorkerSettings
