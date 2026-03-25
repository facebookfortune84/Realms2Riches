from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

# Defer initialization for test mode or if not in production and no explicit URL
if settings.TEST_MODE and not settings.db_config.url.startswith("sqlite+aiosqlite"): # Allow async SQLite for specific tests if configured
    engine = None 
    AsyncSessionLocal = None
    logger.warning("Database engine/session initialization skipped in TEST_MODE for sync DB operations.")
else:
    db_url_from_config = settings.db_config.url
    if db_url_from_config:
        DATABASE_URL = db_url_from_config
    else:
        DATABASE_URL = f"postgresql+asyncpg://{settings.db_config.user}:{settings.db_config.password}@{settings.db_config.host}:{settings.db_config.port}/{settings.db_config.db}"

    # Ensure correct driver for async. If SQLite is forced in settings, use aiosqlite
    if DATABASE_URL.startswith("sqlite://") and not DATABASE_URL.startswith("sqlite+aiosqlite"):
        DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")

    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL debugging
        future=True,
        pool_pre_ping=True,
        pool_size=20,  # Adjust pool size based on expected load
        max_overflow=10
    )

    AsyncSessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

Base = declarative_base()

async def get_db():
    if AsyncSessionLocal is None:
        raise RuntimeError("AsyncSessionLocal not initialized. Not in appropriate DB mode.")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    if engine is None:
        logger.warning("Database initialization skipped. Ensure you are in a valid DB environment.")
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ensured/created successfully.")
