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

class SQLStore:
    def __init__(self, db_url: str = None):
        self.url = db_url or settings.DATABASE_URL
        if not self.url or ("postgresql" in self.url and "localhost" in self.url):
             self.url = "sqlite:///./orchestrator.db"
        
        self.engine = create_engine(self.url)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self._manual_migrate() # Ensure columns exist
        logger.info(f"SQLStore connected to {self.url}")

    def _manual_migrate(self):
        """Force add columns if they don't exist in the current session."""
        if "sqlite" in self.url:
            import sqlite3
            db_path = self.url.replace("sqlite:///", "")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cols = ["tier", "founding_node"]
            for col in cols:
                try:
                    cursor.execute(f"ALTER TABLE user_balances ADD COLUMN {col} TEXT DEFAULT 'BASIC'" if col == "tier" else f"ALTER TABLE user_balances ADD COLUMN {col} INTEGER DEFAULT 0")
                except: pass
            conn.close()

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
