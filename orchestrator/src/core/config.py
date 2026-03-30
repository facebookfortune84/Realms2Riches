import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from orchestrator.src.validation.schemas import DatabaseConfig, MarketingConfig

class Settings(BaseSettings):
    # Detect environment mode - Last file in list has highest priority
    model_config = SettingsConfigDict(
        env_file=[".env.example", ".env.local", ".env.prod", ".env.test", ".env"], 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    # --- CORE ---
    DATABASE_URL: Optional[str] = None
    BACKEND_URL: str = "https://api.realms2riches.com"
    FRONTEND_URL: str = "https://realms2riches.com"
    REALM_MASTER_KEY: str = "placeholder_key"
    ENV_MODE: str = "dev"
    TEST_MODE: bool = False # Flag to indicate if running in test environment
    ANALYTICS_ENABLED: bool = False # Flag to enable/disable analytics events
    BRAND_NAME: str = "Realms 2 Riches"
    PRODUCT_NAME: str = "Sovereign Swarm"
    MARKETING_SITE_URL: str = "https://realms2riches.com"
    CONTACT_EMAIL: str = "robert.demotto@realms2riches.com"

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

    # --- IONOS CLOUD API ---
    IONOS_PUBLIC_PREFIX: Optional[str] = None
    IONOS_SECRET: Optional[str] = None

    # --- SYNTHESIS & VOICE ---
    VOICE_ENABLED: bool = True
    STT_PROVIDER: str = "openai"
    TTS_PROVIDER: str = "elevenlabs"
    ELEVENLABS_API_KEY: Optional[str] = None

    # --- MONETIZATION ---
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_TEST_MODE: bool = False # Flag to use Stripe test keys (for local dev/tests)


    # --- SOCIAL MEDIA ---
    FACEBOOK_PAGE_ACCESS_TOKEN: Optional[str] = None
    FACEBOOK_PAGE_ID: Optional[str] = None
    LINKEDIN_ACCESS_TOKEN: Optional[str] = None
    LINKEDIN_PROFILE_URN: Optional[str] = None
    LINKEDIN_REFRESH_TOKEN: Optional[str] = None
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    X_ACCESS_TOKEN: Optional[str] = None
    SOCIAL_TWITTER_HANDLE: str = "@Realms2Riches"
    SOCIAL_LINKEDIN_URL: str = "https://linkedin.com/company/realms2riches"
    SOCIAL_YOUTUBE_URL: str = "https://youtube.com/c/realms2riches"
    SOCIAL_GITHUB_URL: str = "https://github.com/realms2riches"

    # --- RELIABILITY & OBSERVABILITY ---
    TELEMETRY_ENABLED: bool = True
    CIRCUIT_BREAKER_THRESHOLD: int = 5
    RECOVERY_TIMEOUT: int = 60
    TASK_QUEUE_MAX_SIZE: int = 1000

    # --- MONETIZATION & SAFETY SWITCHES ---
    OUTREACH_ENABLED: bool = False
    DRY_RUN_MODE: bool = True
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    OUTREACH_TEST_RECIPIENT: str = "robert.demotto@realms2riches.com"

    # --- PROPERTIES ---
    def validate_monetization_config(self):
        """Ensures all required Stripe variables are present for live mode, or test mode config is correct."""
        if self.TEST_MODE:
            # In test mode, we expect test keys or will use mocks.
            # If STRIPE_TEST_MODE is true, we assume test keys are provided.
            # If STRIPE_TEST_MODE is false, we expect API keys to be placeholder or mocked.
            pass
        elif self.ENV_MODE == "prod":
            missing = []
            if not self.STRIPE_API_KEY or "sk_live_change_me" in self.STRIPE_API_KEY:
                missing.append("STRIPE_API_KEY")
            if not self.STRIPE_WEBHOOK_SECRET or "whsec_change_me" in self.STRIPE_WEBHOOK_SECRET:
                missing.append("STRIPE_WEBHOOK_SECRET")
            if not self.STRIPE_PUBLISHABLE_KEY or "pk_live_change_me" in self.STRIPE_PUBLISHABLE_KEY:
                missing.append("STRIPE_PUBLISHABLE_KEY")
            
            if missing:
                raise ValueError(f"CRITICAL: Monetization config incomplete in PROD. Missing: {', '.join(missing)}")
        
        # If STRIPE_TEST_MODE is explicitly enabled, ensure keys are test keys
        if self.STRIPE_TEST_MODE:
            if self.STRIPE_API_KEY and not self.STRIPE_API_KEY.startswith("sk_test"):
                 raise ValueError("CRITICAL: STRIPE_TEST_MODE is True but STRIPE_API_KEY is not a test key.")
            if self.STRIPE_PUBLISHABLE_KEY and not self.STRIPE_PUBLISHABLE_KEY.startswith("pk_test"):
                 raise ValueError("CRITICAL: STRIPE_TEST_MODE is True but STRIPE_PUBLISHABLE_KEY is not a test key.")

    def validate_outreach_config(self):
        """Ensures SMTP is ready if outreach is enabled."""
        if self.OUTREACH_ENABLED and not self.DRY_RUN_MODE:
            if not self.SMTP_USER or not self.SMTP_PASS:
                raise ValueError("CRITICAL: OUTREACH_ENABLED is True but SMTP credentials are missing.")

    @property
    def db_config(self) -> DatabaseConfig:
        host = self.POSTGRES_HOST
        # Conscious Fallback for local execution vs docker
        if host in ["postgres", "db"] and os.name == "nt": 
            host = "localhost"
            
        db_url = self.DATABASE_URL
        if db_url and os.name == "nt":
            # Swap known docker host names with localhost in the URL string
            db_url = db_url.replace("@postgres:", "@localhost:").replace("@db:", "@localhost:")

        return DatabaseConfig(
            POSTGRES_USER=self.POSTGRES_USER,
            POSTGRES_PASSWORD=self.POSTGRES_PASSWORD,
            POSTGRES_DB=self.POSTGRES_DB,
            POSTGRES_HOST=host,
            POSTGRES_PORT=self.POSTGRES_PORT,
            DATABASE_URL=db_url
        )

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

settings = Settings()

