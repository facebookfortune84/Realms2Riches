import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
from orchestrator.src.validation.schemas import DatabaseConfig, MarketingConfig

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Marketing & Brand
    BRAND_NAME: str = "My Brand"
    PRODUCT_NAME: str = "My Product"
    MARKETING_SITE_URL: str = "https://example.com"
    CONTACT_EMAIL: str = "hello@example.com"
    SOCIAL_TWITTER_HANDLE: str = "mybrand"
    SOCIAL_LINKEDIN_URL: str = "https://linkedin.com/company/mybrand"
    SOCIAL_YOUTUBE_URL: str = "https://youtube.com/c/mybrand"
    SOCIAL_GITHUB_URL: str = "https://github.com/mybrand"

    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    # LLM
    GROQ_API_KEY: str = "placeholder"
    GROQ_MODEL: str = "llama3-8b-8192"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    
    # Voice
    VOICE_ENABLED: bool = False
    STT_PROVIDER: str = "mock"
    TTS_PROVIDER: str = "mock"
    
    # New discovered keys
    REALM_MASTER_KEY: Optional[str] = None
    REALM_FORGE_API_KEY: Optional[str] = None
    ENCRYPTION_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    LINER_API_KEY: Optional[str] = None # Assuming LINEAR_API_KEY from scan
    
    @property
    def marketing_config(self) -> MarketingConfig:
        return MarketingConfig(
            BRAND_NAME=self.BRAND_NAME,
            PRODUCT_NAME=self.PRODUCT_NAME,
            MARKETING_SITE_URL=self.MARKETING_SITE_URL,
            CONTACT_EMAIL=self.CONTACT_EMAIL,
            SOCIAL_TWITTER_HANDLE=self.SOCIAL_TWITTER_HANDLE,
            SOCIAL_LINKEDIN_URL=self.SOCIAL_LINKEDIN_URL,
            SOCIAL_YOUTUBE_URL=self.SOCIAL_YOUTUBE_URL,
            SOCIAL_GITHUB_URL=self.SOCIAL_GITHUB_URL
        )

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

settings = Settings()
