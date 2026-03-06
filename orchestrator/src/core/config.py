import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from orchestrator.src.validation.schemas import DatabaseConfig, MarketingConfig

class Settings(BaseSettings):
    # Detect environment mode - Last file in list has highest priority
    model_config = SettingsConfigDict(
        env_file=[".env.example", ".env.prod", ".env.local"], 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    # --- CORE ---
    DATABASE_URL: Optional[str] = None
    FRONTEND_URL: str = "http://localhost:5173"
    REALM_MASTER_KEY: str = "placeholder_key"
    ENV_MODE: str = "dev"
    BRAND_NAME: str = "Realms 2 Riches"
    PRODUCT_NAME: str = "Sovereign Swarm"
    MARKETING_SITE_URL: str = "https://www.realmstoriches.xyz"
    CONTACT_EMAIL: str = "robertdemottojr50@gmail.com"

    # --- DATABASE ---
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    
    # --- INTELLIGENCE (Groq / OpenAI) ---
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    
    OPENAI_API_KEY: Optional[str] = None
    
    # --- COMMUNICATION ---
    SMTP_USER: Optional[str] = None
    SMTP_PASS: Optional[str] = None
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    
    # --- SYNTHESIS & VOICE ---
    VOICE_ENABLED: bool = True
    STT_PROVIDER: str = "openai"
    TTS_PROVIDER: str = "elevenlabs"
    ELEVENLABS_API_KEY: Optional[str] = None
    
    # --- MONETIZATION ---
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # --- SOCIAL MEDIA ---
    FACEBOOK_PAGE_TOKEN: Optional[str] = None
    FACEBOOK_PAGE_ID: Optional[str] = None
    LINKEDIN_ACCESS_TOKEN: Optional[str] = None
    LINKEDIN_PROFILE_URN: Optional[str] = None
    LINKEDIN_REFRESH_TOKEN: Optional[str] = None
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    X_ACCESS_TOKEN: Optional[str] = None

    # --- RELIABILITY & OBSERVABILITY ---
    TELEMETRY_ENABLED: bool = True
    CIRCUIT_BREAKER_THRESHOLD: int = 5
    RECOVERY_TIMEOUT: int = 60
    TASK_QUEUE_MAX_SIZE: int = 1000

    # --- PROPERTIES ---
    @property
    def db_config(self) -> DatabaseConfig:
        host = self.POSTGRES_HOST
        # Conscious Fallback for local execution vs docker
        if host == "postgres" and os.name == "nt": 
            host = "localhost"
            
        return DatabaseConfig(
            POSTGRES_USER=self.POSTGRES_USER,
            POSTGRES_PASSWORD=self.POSTGRES_PASSWORD,
            POSTGRES_DB=self.POSTGRES_DB,
            POSTGRES_HOST=host,
            POSTGRES_PORT=self.POSTGRES_PORT,
            DATABASE_URL=self.DATABASE_URL
        )

    @property
    def marketing_config(self) -> MarketingConfig:
        return MarketingConfig(
            BRAND_NAME=self.BRAND_NAME,
            PRODUCT_NAME=self.PRODUCT_NAME,
            MARKETING_SITE_URL=self.MARKETING_SITE_URL,
            CONTACT_EMAIL=self.CONTACT_EMAIL
        )

settings = Settings()
