from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from orchestrator.src.core.database import Base # Import Base from the database module

class LeadStatus(str, enum.Enum):
    NEW = "new"
    SCRAPED = "scraped"
    ENRICHED = "enriched"
    QUEUED = "queued"
    CONTACTED = "contacted"
    REPLIED = "replied"
    CONVERTED = "converted"
    BLACKLISTED = "blacklisted"

class OutreachChannel(str, enum.Enum):
    EMAIL = "email"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    PHONE = "phone"

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    company = Column(String, nullable=True)
    linkedin_url = Column(String, unique=True, nullable=True)
    website = Column(String, nullable=True)
    status = Column(String, default=LeadStatus.NEW)
    source = Column(String, default="manual")
    
    industry = Column(String, nullable=True)
    location = Column(String, nullable=True)
    meta_data = Column(JSON, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    outreach_logs = relationship("OutreachLog", back_populates="lead")

class OutreachLog(Base):
    __tablename__ = "outreach_logs"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    channel = Column(String, default=OutreachChannel.EMAIL)
    status = Column(String)
    subject = Column(String, nullable=True)
    content_hash = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    smtp_account_used = Column(String, nullable=True)
    
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    lead = relationship("Lead", back_populates="outreach_logs")

class SmtpAccount(Base):
    __tablename__ = "smtp_accounts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    smtp_server = Column(String, default="smtp.gmail.com")
    smtp_port = Column(Integer, default=587)
    daily_limit = Column(Integer, default=50)
    sent_today = Column(Integer, default=0)
    last_used = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

class TaskResult(Base):
    __tablename__ = "task_results"
    
    id = Column(String, primary_key=True)
    task_name = Column(String)
    status = Column(String)
    result = Column(JSON, nullable=True)
    error_details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

# --- NEW MODELS FOR AFFILIATE TRACKING ---

class Affiliate(Base):
    __tablename__ = "affiliates"

    id = Column(Integer, primary_key=True, index=True)
    unique_code = Column(String, unique=True, index=True) # e.g., "R2R_PARTNER_XYZ"
    name = Column(String)
    contact_email = Column(String, nullable=True)
    website = Column(String, nullable=True)
    commission_rate = Column(Float, nullable=True) # e.g., 0.10 for 10%
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    clicks = relationship("AffiliateClick", back_populates="affiliate")
    commissions = relationship("Commission", back_populates="affiliate")

class AffiliateClick(Base):
    __tablename__ = "affiliate_clicks"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id"))
    clicked_at = Column(DateTime(timezone=True), server_default=func.now())
    target_url = Column(String) # The URL the user was redirected to
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)

    affiliate = relationship("Affiliate", back_populates="clicks")

class Commission(Base):
    __tablename__ = "commissions"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id"))
    sale_id = Column(String, index=True) # e.g., Stripe charge ID or session ID
    amount = Column(Float) # Amount of commission earned
    currency = Column(String, default="USD")
    attributed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    affiliate = relationship("Affiliate", back_populates="commissions")

class Project(Base):
    """
    Represents an autonomously generated application (Famous.ai style).
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    slug = Column(String, unique=True, index=True)
    
    # Architecture
    tech_stack = Column(JSON, default={"frontend": "react", "backend": "python", "db": "postgres"})
    features = Column(JSON, default=[])
    
    # Paths
    local_path = Column(String, nullable=True) # Where the code lives on disk
    repo_url = Column(String, nullable=True)
    
    # Status
    status = Column(String, default="draft") # draft, building, deployed, failed
    deployment_url = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

