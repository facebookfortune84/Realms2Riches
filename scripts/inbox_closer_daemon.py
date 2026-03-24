import asyncio
import os
import sys
import json
import logging
import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Ensure imports work
sys.path.append(os.getcwd())

from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.core.llm_provider import llm_provider
from orchestrator.src.tools.smtp_tools import get_smtp_tools # Assuming this tool is correctly set up
from orchestrator.src.core.database import AsyncSessionLocal # For potential DB updates (e.g., blacklisting)
from orchestrator.src.core.models import Lead, LeadStatus # For updating lead status

logger = get_logger("INBOX_CLOSER")

SLEEP_INTERVAL = 600  # Check every 10 minutes

class InboxCloserDaemon:
    def __init__(self):
        # Load SMTP tool - assuming 'smtp_outreach' is the correct tool ID
        self.smtp_tool = get_smtp_tools().get("smtp_outreach")
        if not self.smtp_tool:
            logger.error("SMTP tool 'smtp_outreach' not found. Email replies may fail.")

        # Load IMAP credentials securely from settings
        self.imap_server = settings.IMAP_SERVER
        self.imap_user = settings.IMAP_USER
        self.imap_pass = settings.IMAP_PASS # Should be securely stored/loaded from .env.prod

    async def check_inbox(self) -> List[Dict]:
        """
        Connects to the IMAP server, fetches recent emails, and processes replies.
        Requires IMAP credentials to be configured in .env.prod.
        """
        replies = []
        if not all([self.imap_server, self.imap_user, self.imap_pass]):
            logger.warning("IMAP credentials not fully configured in environment settings. Skipping inbox check.")
            return replies

        try:
            logger.info(f"Connecting to IMAP server: {self.imap_server}")
            mail = imaplib.IMAP4_SSL(self.imap_server)
            await asyncio.to_thread(mail.login, self.imap_user, self.imap_pass)
            await asyncio.to_thread(mail.select, 'inbox')

            # Search for recent emails (e.g., last 7 days)
            # Adjust search criteria as needed (e.g., specific subject lines, FROM addresses)
            # Using 'UNSEEN' to process only new emails is often a good strategy.
            # For now, searching broadly for recent emails to ensure capture.
            # Define date threshold for recent emails (e.g., last 7 days)
            seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%d-%b-%Y')
            search_criteria = f'(SINCE "{seven_days_ago}")' 
            
            typ, data = await asyncio.to_thread(mail.search, None, search_criteria)
            
            email_ids = data[0].split()

            # Process a limited number of emails to avoid overwhelming the system
            # and to manage potential long-running operations.
            for email_id in email_ids[-50:]: # Process last 50 emails
                logger.debug(f"Fetching email ID: {email_id.decode()}")
                typ, msg_data = await asyncio.to_thread(mail.fetch, email_id, '(RFC822)')
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Decode email subject and sender
                        try:
                            subject, encoding = decode_header(msg["Subject"])[0]
                            decoded_subject = subject.decode(encoding if isinstance(encoding, str) else 'utf-8', errors='ignore') if isinstance(subject, bytes) else subject
                        except Exception as e:
                            decoded_subject = msg["Subject"] # Fallback if decoding fails
                            logger.warning(f"Could not decode subject for email ID {email_id.decode()}: {e}")

                        from_ = msg["From"]
                        
                        logger.debug(f"Processing email from: {from_} with subject: {decoded_subject}")

                        # Extract sender email address reliably
                        sender_email = None
                        if from_:
                            match = re.search(r'<([^>]+)>', from_)
                            sender_email = match.group(1) if match else from_
                        
                        # Find the plain text body part
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                ctype = part.get_content_type()
                                cdispo = str(part.get('Content-Disposition'))
                                if ctype == 'text/plain' and 'attachment' not in cdispo:
                                    payload = part.get_payload(decode=True)
                                    try:
                                        body = payload.decode(part.get_content_charset() or 'utf-8')
                                    except (UnicodeDecodeError, TypeError):
                                        body = str(payload) # Fallback if decoding fails
                                    break # Found the text/plain part
                        else:
                            # Not multipart, assume it's plain text
                            payload = msg.get_payload(decode=True)
                            try:
                                body = payload.decode(msg.get_content_charset() or 'utf-8')
                            except (UnicodeDecodeError, TypeError):
                                body = str(payload)

                        if body and sender_email:
                            replies.append({"email": sender_email, "text": body, "subject": decoded_subject})
                            # Mark email as SEEN after successful processing to avoid reprocessing
                            await asyncio.to_thread(mail.store, email_id, '+FLAGS', '\Seen')

            await asyncio.to_thread(mail.close)
            await asyncio.to_thread(mail.logout)

        except imaplib.IMAP4.error as imap_err:
            logger.error(f"IMAP error during connection or operation: {imap_err}")
        except Exception as e:
            logger.error(f"An unexpected error occurred checking inbox: {e}")
        
        return replies

    async def classify_sentiment(self, text: str) -> str:
        """Classifies the sentiment of the email reply using an LLM."""
        prompt = f"""
        Classify the sentiment of this email reply: '{text}'. 
        Categories: POSITIVE, OBJECTION, UNSUBSCRIBE, NEUTRAL. 
        Return only the category name.
        """
        try:
            # Use the globally available llm_provider
            sentiment = await asyncio.to_thread(llm_provider.generate_text, prompt)
            return sentiment.strip().upper()
        except Exception as e:
            logger.error(f"LLM sentiment classification failed: {e}")
            return "NEUTRAL" # Default sentiment on failure

    async def handle_reply(self, email: str, text: str, subject: str):
        """Processes a parsed email reply based on its sentiment classification."""
        sentiment = await self.classify_sentiment(text)
        logger.info(f"📬 Reply from {email} (Subject: {subject}): {sentiment}")
        
        reply_body = ""
        if "POSITIVE" in sentiment:
            # Link to Genesis Forge or specific product purchase based on context
            reply_body = f"""
            <html>
            <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
                <p>Hello,</p>
                <p>That's fantastic to hear! We're excited to help you launch your Sovereign AI Swarm.</p>
                <p>You can get started by configuring your custom swarm here: <a href="{settings.FRONTEND_URL}/genesis" style="color: #007bff; text-decoration: none; font-weight: bold;">Access Genesis Forge</a></p>
                <p>We'll be in touch shortly to finalize your setup.</p>
                <p>Best regards,<br>The Realms2Riches Team</p>
            </body>
            </html>
            """
        elif "OBJECTION" in sentiment:
            reply_body = """
            <html>
            <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
                <p>Hello,</p>
                <p>I understand your concern regarding the initial investment. Many of our successful partners shared similar hesitations.</p>
                <p>However, they found that the projected ROI from the autonomous revenue streams often offset the cost within months. Would you be open to a brief 5-minute call to explore the data behind this?</p>
                <p>Best regards,<br>The Realms2Riches Team</p>
            </body>
            </html>
            """
        elif "UNSUBSCRIBE" in sentiment:
            logger.info(f"🚫 User requested to unsubscribe or is no longer interested: {email}")
            # Add logic to unsubscribe user, e.g., update Lead status to BLACKLISTED
            async with AsyncSessionLocal() as session:
                lead = await session.scalar(select(Lead).where(Lead.email == email))
                if lead:
                    lead.status = LeadStatus.BLACKLISTED
                    await session.commit()
                    logger.info(f"Lead {email} marked as BLACKLISTED.")
            return # Do not reply if unsubscribed

        if reply_body and self.smtp_tool:
            try:
                # Execute SMTP tool for sending reply
                await self.smtp_tool.execute(
                    target_email=email,
                    subject=f"Re: {subject}", # Reply subject
                    html_body=reply_body
                )
                logger.info(f"✉️ Replied to {email} regarding '{subject}' with sentiment '{sentiment}'.")
            except Exception as e:
                logger.error(f"Failed to send reply email to {email}: {e}")
        else:
            logger.warning(f"No reply body generated or SMTP tool not available for sentiment: {sentiment}")

    async def run(self):
        """Main loop for the daemon."""
        logger.info("🚀 INBOX CLOSER DAEMON STARTED (Monitoring for replies...)")
        while True:
            try:
                # Fetch and process recent emails
                replies = await self.check_inbox()
                if replies:
                    for r in replies:
                        await self.handle_reply(r['email'], r['text'], r['subject'])
                else:
                    logger.debug("No new relevant emails found.")
            except Exception as e:
                logger.error(f"Error in main daemon loop: {e}")
            
            await asyncio.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    # This block allows running the daemon directly for testing or as a separate process.
    # For production, it's typically managed by Docker Compose and SOVEREIGN_START.ps1.
    daemon = InboxCloserDaemon()
    try:
        asyncio.run(daemon.run())
    except KeyboardInterrupt:
        logger.info("🛑 Inbox Closer Daemon stopped by user.")
    except Exception as e:
        logger.error(f"Daemon failed to run: {e}")
