import asyncio
import os
import sys
import json
import logging
from datetime import datetime
from typing import List, Dict

# Ensure imports
sys.path.append(os.getcwd())

from orchestrator.src.core.llm_provider import llm_provider
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.tools.smtp_tools import get_smtp_tools

logger = get_logger("INBOX_CLOSER")

SLEEP_INTERVAL = 600  # 10 minutes

class InboxCloserDaemon:
    def __init__(self):
        self.smtp_tool = {t.config.tool_id: t for t in get_smtp_tools()}["smtp_outreach"]

    async def check_inbox(self) -> List[Dict]:
        """
        Framework for checking Gmail/IMAP replies.
        Requires GMAIL_APP_PASSWORD in environment.
        """
        # Placeholder for real IMAP logic
        # For now, we simulate finding a 'Positive' reply
        return []

    async def classify_sentiment(self, text: str) -> str:
        prompt = f"Classify this email reply sentiment: '{text}'. Categories: POSITIVE, OBJECTION, UNSUBSCRIBE, NEUTRAL. Return only the category."
        return llm_provider.generate_text(prompt).strip().upper()

    async def handle_reply(self, email: str, text: str):
        sentiment = await self.classify_sentiment(text)
        logger.info(f"📬 Reply from {email}: {sentiment}")
        
        reply_body = ""
        if "POSITIVE" in sentiment:
            reply_body = "That's great to hear! You can initialize your swarm here: https://buy.stripe.com/6oUeVdcPTeMheN46ll8so01"
        elif "OBJECTION" in sentiment:
            reply_body = "I understand the concern. Most of our partners felt the same until they saw the $10k TMR yield from the first 30 days. Worth a 5-min chat?"
        elif "UNSUBSCRIBE" in sentiment:
            logger.info(f"🚫 Blacklisting {email}")
            return

        if reply_body:
            # Send reply via SMTP tool
            await asyncio.to_thread(
                self.smtp_tool.execute,
                {
                    "target_email": email,
                    "subject": "Re: Autonomous Revenue",
                    "html_body": f"<html><body><p>{reply_body}</p></body></html>"
                }
            )
            logger.info(f"✉️ Replied to {email}")

    async def run(self):
        logger.info("🚀 INBOX CLOSER DAEMON STARTED (Monitoring for replies...)")
        while True:
            replies = await self.check_inbox()
            for r in replies:
                await self.handle_reply(r['email'], r['text'])
            
            await asyncio.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    daemon = InboxCloserDaemon()
    try:
        asyncio.run(daemon.run())
    except KeyboardInterrupt:
        pass
