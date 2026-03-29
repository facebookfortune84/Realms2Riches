import os
from sqlalchemy import create_engine, Column, String, DateTime, JSON, Float, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)
Base = declarative_base()

class RunRecord(Base):
    __tablename__ = 'runs'
    id = Column(String, primary_key=True)
    project_id = Column(String, index=True)
    agent_id = Column(String)
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON)

class ProfitRecord(Base):
    __tablename__ = 'profit_ledger'
    id = Column(String, primary_key=True)
    type = Column(String) # 'revenue', 'expense'
    category = Column(String) # 'sale', 'api_cost', 'fee'
    amount = Column(Float)
    currency = Column(String, default='USD')
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON)

class UserBalance(Base):
    __tablename__ = 'user_balances'
    user_id = Column(String, primary_key=True)
    balance = Column(Float, default=0.0)
    credits = Column(Integer, default=0)
    tier = Column(String, default='BASIC') # BASIC, PRO, SOVEREIGN
    founding_node = Column(Integer, default=0) 
    last_updated = Column(DateTime, default=datetime.utcnow)

class UsageRecord(Base):
    __tablename__ = 'usage_ledger'
    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    agent_id = Column(String)
    tokens = Column(Integer)
    cost = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class AnalyticsEvent(Base):
    __tablename__ = 'analytics_events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String, index=True)
    product_id = Column(String, nullable=True)
    campaign_id = Column(String, nullable=True)
    user_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON)

class SQLStore:
    def __init__(self, db_url: str = None):
        # Prefer provided URL, then config setting
        self.url = db_url or settings.db_config.url
        
        # --- Reliability & Scaling: DB Strictness ---
        if settings.TEST_MODE:
            self.url = "sqlite:///./test_orchestrator.db" # Force test DB in test mode
            logger.info("SQLStore operating in TEST_MODE with dedicated SQLite database.")
        elif settings.ENV_MODE == "prod":
            if "sqlite://" in self.url:
                raise ValueError("CRITICAL: SQLite is not allowed in production environment. Configure PostgreSQL.")
            logger.info("SQLStore operating in PROD_MODE with PostgreSQL.")
        elif not self.url or "sqlite://" in self.url:
             # Critical fallback for initial dev setup only
             self.url = "sqlite:///./orchestrator.db"
             logger.warning("SQLStore falling back to SQLite. Ensure POSTGRES_URL is set for production.")
        
        # Ensure we use the sync driver for this synchronous class
        if "postgresql+asyncpg" in self.url:
            self.url = self.url.replace("postgresql+asyncpg", "postgresql")
        
        # Handle Windows local dev vs Docker host naming
        if "localhost" not in self.url and "127.0.0.1" not in self.url and os.name == "nt":
            # If running on windows but trying to hit 'db' (docker name), we might need to swap to localhost
            # But in prod (.env.prod), DATABASE_URL usually points to the docker network 'db'
            # Settings.db_config already handles this via pydantic properties
            pass

        try:
            self.engine = create_engine(self.url)
            self.Session = sessionmaker(bind=self.engine)
            Base.metadata.create_all(self.engine)
            logger.info(f"SQLStore connected to {self.url.split('@')[-1]}") # Log host only for security
        except Exception as e:
            logger.error(f"Failed to connect to primary DB: {e}")
            # Fallback to sqlite
            self.url = "sqlite:///./orchestrator.db"
            self.engine = create_engine(self.url)
            self.Session = sessionmaker(bind=self.engine)
            Base.metadata.create_all(self.engine)
            logger.warning("SQLStore running in FALLBACK (SQLite) mode.")

    def add_run(self, run_data: dict):
        session = self.Session()
        try:
            record = RunRecord(**run_data)
            session.add(record)
            session.commit()
        finally:
            session.close()

    def add_profit_entry(self, entry: dict):
        session = self.Session()
        try:
            record = ProfitRecord(**entry)
            session.add(record)
            session.commit()
        finally:
            session.close()

    def add_analytics_event(self, event_data: dict):
        session = self.Session()
        try:
            record = AnalyticsEvent(**event_data)
            session.add(record)
            session.commit()
        finally:
            session.close()

    def update_user_balance(self, user_id: str, amount: float, credits: int = 0):
        session = self.Session()
        try:
            user = session.query(UserBalance).filter_by(user_id=user_id).first()
            if not user:
                user = UserBalance(user_id=user_id, balance=amount, credits=credits)
                session.add(user)
            else:
                user.balance += amount
                user.credits += credits
                user.last_updated = datetime.utcnow()
            session.commit()
        finally:
            session.close()

    def get_user_balance(self, user_id: str) -> dict:
        session = self.Session()
        try:
            user = session.query(UserBalance).filter_by(user_id=user_id).first()
            if user:
                return {
                    "balance": user.balance, 
                    "credits": user.credits, 
                    "tier": user.tier,
                    "founding_node": bool(user.founding_node)
                }
            return {"balance": 0.0, "credits": 0, "tier": "BASIC", "founding_node": False}
        finally:
            session.close()

    def get_total_profit(self) -> float:
        session = self.Session()
        try:
            entries = session.query(ProfitRecord).all()
            rev = sum([e.amount for e in entries if e.type == 'revenue'])
            exp = sum([e.amount for e in entries if e.type == 'expense'])
            return rev - exp
        finally:
            session.close()
