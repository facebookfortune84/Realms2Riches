from pydantic_settings import BaseSettings, SettingsConfigDict

class OutreachSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.prod", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    # --- SAFETY SWITCHES ---
    OUTREACH_ENABLED: bool = False
    OUTREACH_DRY_RUN: bool = True

    # --- LIMITS ---
    DAILY_SEND_LIMIT: int = 50
    PER_DOMAIN_LIMIT: int = 5
    MIN_DELAY_SECONDS: int = 60
    MAX_DELAY_SECONDS: int = 300

    # --- REDIS / ARQ ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- TEST RECIPIENT ---
    OUTREACH_TEST_RECIPIENT: str = "robert.demotto@realms2riches.com"

outreach_settings = OutreachSettings()
