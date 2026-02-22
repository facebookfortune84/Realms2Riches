import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from orchestrator.src.validation.schemas import DatabaseConfig, MarketingConfig

class Settings(BaseSettings):
    # Detect environment mode
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env.prod"), 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    # --- CORE ---
    DATABASE_URL: str = "sqlite:///./orchestrator.db"
    FRONTEND_URL: str = "http://localhost:5173"
    REALM_MASTER_KEY: str = "placeholder_key"
    ENV_MODE: str = "dev"

    # --- DATABASE ---
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432

    # --- INTELLIGENCE (Groq / OpenAI) ---
    GROQ_API_KEY: Optional[str] = "placeholder"
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    
    OPENAI_API_KEY: Optional[str] = None
    
    # --- COMMUNICATION ---
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    SENDGRID_API_KEY: Optional[str] = None
    WHATSAPP_TOKEN: Optional[str] = None
    
    # --- SOCIAL ---
    LINKEDIN_ACCESS_TOKEN: Optional[str] = None
    LINKEDIN_REFRESH_TOKEN: Optional[str] = None
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    FACEBOOK_PAGE_TOKEN: Optional[str] = None
    FACEBOOK_PAGE_ID: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None
    LINKEDIN_PROFILE_URN: Optional[str] = None
    
    # --- SYNTHESIS & VOICE ---
    VOICE_ENABLED: bool = True
    STT_PROVIDER: str = "mock"
    TTS_PROVIDER: str = "mock"
    ELEVENLABS_API_KEY: Optional[str] = None
    STABILITY_API_KEY: Optional[str] = None
    
    # --- MONETIZATION ---
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # --- PROPERTIES ---
    @property
    def db_config(self) -> DatabaseConfig:
        return DatabaseConfig(
            POSTGRES_USER=self.POSTGRES_USER,
            POSTGRES_PASSWORD=self.POSTGRES_PASSWORD,
            POSTGRES_DB=self.POSTGRES_DB,
            POSTGRES_HOST=self.POSTGRES_HOST,
            POSTGRES_PORT=self.POSTGRES_PORT,
            DATABASE_URL=self.DATABASE_URL
        )

    @property
    def marketing_config(self) -> MarketingConfig:
        return MarketingConfig(
            brand_name="Realms 2 Riches",
            product_name="Sovereign Swarm",
            website_url="https://frontend-two-xi-gal9lkptfi.vercel.app/",
            contact_email="hello@glowfly-sizeable-lazaro.ngrok-free.dev",
            twitter_handle="realms2riches",
            linkedin_url="https://linkedin.com/company/realms2riches",
            youtube_url="https://youtube.com/@realms2riches",
            github_url="https://github.com/realms2riches"
        )

settings = Settings()
