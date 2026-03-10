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
    last_updated = Column(DateTime, default=datetime.utcnow)

class SQLStore:
    def __init__(self, db_url: str = None):
        # 1. Try provided URL
        # 2. Try settings (Postgres)
        # 3. Fallback to local SQLite
        urls_to_try = [
            db_url,
            settings.db_config.connection_url,
            "sqlite:///./orchestrator.db"
        ]
        
        self.engine = None
        for url in urls_to_try:
            if not url: continue
            try:
                engine = create_engine(url)
                # Test connection
                with engine.connect() as conn:
                    pass
                self.engine = engine
                logger.info(f"SQLStore connected to {url.split('@')[-1] if '@' in url else url}")
                break
            except Exception as e:
                logger.warning(f"Failed to connect to {url}: {e}")
        
        if not self.engine:
            # Last resort: local sqlite without testing
            self.engine = create_engine("sqlite:///./orchestrator.db")
            
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_run(self, run_data: dict):
        session = self.Session()
        try:
            record = RunRecord(**run_data)
            session.add(record)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_runs(self, project_id: str):
        session = self.Session()
        try:
            return session.query(RunRecord).filter_by(project_id=project_id).all()
        finally:
            session.close()

    def add_profit_entry(self, entry: dict):
        session = self.Session()
        try:
            record = ProfitRecord(**entry)
            session.add(record)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_total_profit(self) -> float:
        session = self.Session()
        try:
            entries = session.query(ProfitRecord).all()
            revenue = sum([e.amount for e in entries if e.type == 'revenue'])
            expenses = sum([e.amount for e in entries if e.type == 'expense'])
            return revenue - expenses
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
                return {"balance": user.balance, "credits": user.credits}
            return {"balance": 0.0, "credits": 0}
        finally:
            session.close()
