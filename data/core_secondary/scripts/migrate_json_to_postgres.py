import asyncio
import json
import os
import sys
from sqlalchemy.future import select

sys.path.append(os.getcwd())

from orchestrator.src.core.database import AsyncSessionLocal, init_db
from orchestrator.src.core.models import Lead, LeadStatus
from orchestrator.src.logging.logger import get_logger

logger = get_logger("MIGRATION")

async def migrate():
    await init_db()
    
    path = "data/customers/leads.json"
    if not os.path.exists(path):
        logger.info("No leads.json found, skipping migration.")
        return

    with open(path, "r") as f:
        try:
            leads = json.load(f)
        except:
            logger.error("Failed to parse leads.json")
            return

    async with AsyncSessionLocal() as session:
        count = 0
        for l in leads:
            email = l.get("email")
            if not email:
                continue
                
            # Check duplicate
            stmt = select(Lead).where(Lead.email == email)
            result = await session.execute(stmt)
            if result.scalar_one_or_none():
                continue
                
            new_lead = Lead(
                company=l.get("name"),
                email=email,
                website=l.get("website"),
                linkedin_url=l.get("yc_link"), # Assuming this is the best link we have
                status=LeadStatus.NEW,
                meta_data={"description": l.get("description")}
            )
            session.add(new_lead)
            count += 1
            
        await session.commit()
        logger.info(f"✅ Migrated {count} leads to Postgres.")

if __name__ == "__main__":
    asyncio.run(migrate())
