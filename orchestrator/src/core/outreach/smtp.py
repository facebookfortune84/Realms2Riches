import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy import select
from orchestrator.src.core.database import AsyncSessionLocal
from orchestrator.src.core.models import SmtpAccount, OutreachLog, Lead
from orchestrator.src.logging.logger import get_logger
from datetime import datetime, date

logger = get_logger(__name__)

async def get_next_available_smtp_account(session):
    """
    Selects the next available SMTP account that hasn't hit its daily limit.
    Implements a simple Round-Robin or Least-Used strategy.
    """
    today = date.today()
    
    # Reset counts if new day (simple check, better done via scheduled job but this works for now)
    # We won't reset in DB here to avoid complexity, assuming an external cron or just using 'last_used' logic.
    # Actually, let's just query for accounts with sent_today < daily_limit
    # AND (last_used date is today OR last_used is null OR last_used < today)
    
    # Using a simple heuristic: Find active accounts with sent_today < daily_limit
    # We need to handle the "reset daily count" logic. 
    # For now, let's assume 'sent_today' is reset by a separate cron or we check against last_used date.
    
    stmt = select(SmtpAccount).where(
        SmtpAccount.is_active == True
    ).order_by(SmtpAccount.last_used.asc()) # Get the one used longest ago
    
    result = await session.execute(stmt)
    accounts = result.scalars().all()
    
    for account in accounts:
        # Check if we need to reset the counter
        if account.last_used and account.last_used.date() < today:
            account.sent_today = 0
            session.add(account)
            await session.commit() # Commit reset
        
        if account.sent_today < account.daily_limit:
            return account
            
    return None

async def send_cold_email(lead_id: int, subject: str, body_html: str):
    async with AsyncSessionLocal() as session:
        # 1. Get Lead
        lead = await session.get(Lead, lead_id)
        if not lead or not lead.email:
            logger.error(f"Lead {lead_id} not found or has no email.")
            return False

        # 2. Get SMTP Account
        account = await get_next_available_smtp_account(session)
        if not account:
            logger.error("No available SMTP accounts with quota.")
            # Log failure
            log = OutreachLog(
                lead_id=lead_id,
                channel="email",
                status="failed",
                error_message="No SMTP quota available"
            )
            session.add(log)
            await session.commit()
            return False

        # 3. Send Email
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{account.email}" # Can add name alias later
            msg['To'] = lead.email
            msg['Subject'] = subject
            msg.attach(MIMEText(body_html, 'html'))

            # Blocking call, run in executor if needed, but for now simple sync inside async task is okay for low volume
            # For high volume, use aiosmtplib. I'll stick to smtplib for reliability and standard lib usage unless blocking is an issue.
            # Given this runs in a worker process, blocking is acceptable.
            
            with smtplib.SMTP(account.smtp_server, account.smtp_port) as server:
                server.starttls()
                server.login(account.email, account.password)
                server.send_message(msg)

            # 4. Update Logs & Quota
            account.sent_today += 1
            account.last_used = datetime.now()
            
            log = OutreachLog(
                lead_id=lead_id,
                channel="email",
                status="sent",
                subject=subject,
                smtp_account_used=account.email
            )
            
            lead.status = "contacted"
            lead.updated_at = datetime.now()

            session.add(account)
            session.add(log)
            session.add(lead)
            await session.commit()
            
            logger.info(f"Email sent to {lead.email} via {account.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {lead.email}: {e}")
            log = OutreachLog(
                lead_id=lead_id,
                channel="email",
                status="failed",
                error_message=str(e),
                smtp_account_used=account.email
            )
            session.add(log)
            await session.commit()
            return False
