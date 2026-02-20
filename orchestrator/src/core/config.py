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

    # Core
    DATABASE_URL: str = "sqlite:///./orchestrator.db"
    FRONTEND_URL: str = "http://localhost:5173"
    REALM_MASTER_KEY: str = "placeholder_key"

    # Database Fields (for property construction)
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432

    # Intelligence
    GROQ_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Communication
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    SENDGRID_API_KEY: Optional[str] = None
    
    # Social
    LINKEDIN_ACCESS_TOKEN: Optional[str] = None
    FACEBOOK_ACCESS_TOKEN: Optional[str] = None
    
    # Synthesis
    ELEVENLABS_API_KEY: Optional[str] = None
    STABILITY_API_KEY: Optional[str] = None
    
    # Monetization
    STRIPE_API_KEY: Optional[str] = None

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
        # Provide defaults for missing marketing fields
        return MarketingConfig(
            BRAND_NAME="Realms 2 Riches",
            PRODUCT_NAME="Sovereign Swarm",
            MARKETING_SITE_URL=self.FRONTEND_URL,
            CONTACT_EMAIL="hello@realms2riches.ai",
            SOCIAL_TWITTER_HANDLE="realms2riches",
            SOCIAL_LINKEDIN_URL="https://linkedin.com/company/realms2riches",
            SOCIAL_YOUTUBE_URL="https://youtube.com/@realms2riches",
            SOCIAL_GITHUB_URL="https://github.com/realms2riches"
        )

settings = Settings()
