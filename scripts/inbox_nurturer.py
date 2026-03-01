import asyncio
import os
import sys
import json
import base64

sys.path.append(os.getcwd())

from orchestrator.src.core.orchestrator import Orchestrator
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.validation.schemas import ToolInvocation

logger = get_logger("INDUSTRIAL_NURTURER")

async def run_inbox_nurturer():
    logger.info("🕵️ STARTING INDUSTRIAL INBOX NURTURER (FILTERED)...")
    
    orchestrator = Orchestrator()
    await orchestrator.startup()
    
    outreach_tool = orchestrator.cells["GLOBAL_MARKET_FORCE"].agent_pool[0].tools["outreach"]
    service = outreach_tool._get_gmail_service()
    
    # Only target threads related to our pitches
    query = "is:unread label:inbox (Realms2Riches OR Jarvis OR 'Revenue Operations')"
    
    while True:
        try:
            results = service.users().messages().list(userId="me", q=query).execute()
            messages = results.get("messages", [])
            
            if not messages:
                logger.info("📭 No founder replies detected. Monitoring...")
            else:
                for msg in messages:
                    msg_id = msg["id"]
                    full_msg = service.users().messages().get(userId="me", id=msg_id).execute()
                    
                    headers = full_msg["payload"]["headers"]
                    sender = next(h["value"] for h in headers if h["name"] == "From")
                    subject = next(h["value"] for h in headers if h["name"] == "Subject")
                    
                    logger.info(f"🚨 TARGETED REPLY: {sender} | {subject}")
                    
                    # Force the agent to handle the objection/question using Oracle prompts
                    async for step in orchestrator.submit_task_stream(
                        f"OBJECTION_HANDLER: A founder ({sender}) replied to our pitch with subject '{subject}'. Respond with a closing pitch using the Oracle Enterprise prompt structure.", 
                        "nurture_close"
                    ):
                        if step["status"] == "completed":
                            logger.info(f"✅ Professional rebuttal sent to {sender}.")
                    
                    # Mark as read
                    service.users().messages().batchModify(
                        userId="me",
                        body={"ids": [msg_id], "removeLabelIds": ["UNREAD"]}
                    ).execute()
                    
        except Exception as e:
            logger.error(f"Nurturer Loop Error: {e}")

        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(run_inbox_nurturer())
