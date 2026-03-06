import os
import sys
import asyncio
import logging
import smtplib
import json
from email.mime.text import MIMEText
from dotenv import load_dotenv

sys.path.append(os.getcwd())

# FORCE LOAD .env.prod
if os.path.exists(".env.prod"):
    load_dotenv(".env.prod", override=True)

# IMPORT ACTUAL PROJECT CONFIG
from orchestrator.src.core.config import settings

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DEEP_PROBE")

async def probe_stripe():
    if not settings.STRIPE_API_KEY:
        logger.error("❌ STRIPE: Key missing.")
        return False
    try:
        import stripe
        stripe.api_key = settings.STRIPE_API_KEY
        balance = stripe.Balance.retrieve()
        logger.info(f"✅ STRIPE LIVE: Available=${balance['available'][0]['amount']/100}")
        return True
    except Exception as e:
        logger.error(f"❌ STRIPE FAILED: {e}")
        return False

async def probe_groq():
    if not settings.GROQ_API_KEY:
        logger.error("❌ GROQ: Key missing.")
        return False
    try:
        from groq import Groq
        client = Groq(api_key=settings.GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": "System check."}],
            model=settings.GROQ_MODEL,
        )
        logger.info(f"✅ GROQ LIVE: Response received.")
        return True
    except Exception as e:
        logger.error(f"❌ GROQ FAILED: {e}")
        return False

async def probe_database():
    db_cfg = settings.db_config
    url = db_cfg.connection_url
    logger.info(f"Probing DB at {db_cfg.host}...")
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(url, connect_args={'connect_timeout': 5})
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            if result[0] == 1:
                logger.info("✅ POSTGRES LIVE: Connection successful.")
                return True
    except Exception as e:
        logger.error(f"❌ POSTGRES FAILED: {e}")
        return False

async def probe_gmail_api():
    token_file = "data/auth/gmail_token.json"
    if not os.path.exists(token_file):
        return False, "Token file missing"
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request
        creds = Credentials.from_authorized_user_file(token_file)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(token_file, 'w') as token: token.write(creds.to_json())
            else: return False, "Token invalid/revoked"
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        return True, profile.get('emailAddress')
    except Exception as e:
        return False, str(e)

async def probe_smtp():
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    if not user or not password: return False, "Missing creds"
    try:
        # Try 465 SSL first
        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10)
            with server:
                server.login(user, password)
                return True, "465 SSL"
        except:
            # Fallback to 587 STARTTLS
            server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
            server.starttls()
            with server:
                server.login(user, password)
                return True, "587 STARTTLS"
    except Exception as e:
        return False, str(e)

async def grand_audit():
    print("\n🔬 INITIATING COMPREHENSIVE SUCCESS PROBE 🔬")
    print("===============================================")
    
    results = {
        "Stripe": await probe_stripe(),
        "Groq": await probe_groq(),
        "Database": await probe_database(),
    }
    
    # Communication Probe (Gmail API or SMTP)
    api_ok, api_msg = await probe_gmail_api()
    if api_ok:
        results["Communication (Gmail API)"] = True
        logger.info(f"✅ GMAIL API LIVE: {api_msg}")
    else:
        logger.warning(f"⚠️ GMAIL API failed ({api_msg}), falling back to SMTP...")
        smtp_ok, smtp_msg = await probe_smtp()
        if smtp_ok:
            results["Communication (SMTP)"] = True
            logger.info(f"✅ SMTP LIVE: {smtp_msg}")
        else:
            results["Communication"] = False
            logger.error(f"❌ COMMUNICATION FAILED: SMTP also failed ({smtp_msg})")

    print("\n📊 FINAL PROBE RESULTS")
    print("===============================================")
    all_pass = True
    for service, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {service}")
        if not status: all_pass = False
        
    if all_pass:
        print("\n🏆 SYSTEM STATUS: 100% SUCCESS. ALL CHANNELS LIVE.")
    else:
        print("\n⚠️ SYSTEM STATUS: PARTIAL FAILURE. FIX REQUIRED.")

if __name__ == "__main__":
    asyncio.run(grand_audit())
