import sys
import os
sys.path.append(os.getcwd())

import os
from orchestrator.src.core.config import Settings

def test_settings_load():
    """Verify that settings load correctly from environment."""
    # We can't easily mock the pydantic settings file loading without complex patching,
    # but we can verify that the resulting object has the expected attributes.
    from orchestrator.src.core.config import settings
    
    assert settings.DATABASE_URL is not None
    assert settings.ENV_MODE in ["dev", "prod", "test"]
    assert hasattr(settings, "db_config")
    assert hasattr(settings, "marketing_config")

def test_db_config_property():
    """Verify the db_config property logic."""
    # We pass individual fields, and DATABASE_URL=None to ensure it uses the fields
    settings = Settings(
        POSTGRES_USER="test_user",
        POSTGRES_PASSWORD="test_password",
        POSTGRES_DB="test_db",
        POSTGRES_HOST="test_host",
        POSTGRES_PORT=1234,
        DATABASE_URL=None
    )
    
    db_config = settings.db_config
    assert db_config.user == "test_user"
    assert db_config.password == "test_password"
    assert db_config.db == "test_db"
    assert db_config.host == "test_host"
    assert db_config.port == 1234
    assert "test_user:test_password@test_host:1234/test_db" in db_config.connection_url

def test_marketing_config_property():
    """Verify the marketing_config property logic."""
    settings = Settings(
        BRAND_NAME="Test Brand",
        PRODUCT_NAME="Test Product",
        MARKETING_SITE_URL="https://test.com",
        CONTACT_EMAIL="test@test.com"
    )
    m_config = settings.marketing_config
    assert m_config.brand_name == "Test Brand"
    assert m_config.product_name == "Test Product"
    assert m_config.website_url == "https://test.com"
    assert m_config.contact_email == "test@test.com"
