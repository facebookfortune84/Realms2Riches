import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

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

settings = Settings()
