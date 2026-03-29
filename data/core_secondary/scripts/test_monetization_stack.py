import pytest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Ensure project root is in path
sys.path.append(os.getcwd())

from orchestrator.src.core.config import settings
from orchestrator.src.memory.sql_store import SQLStore
from orchestrator.src.core.monetization.engine import MonetizationEngine
from orchestrator.src.core.outreach.config import outreach_settings

# --- Fixtures for clean state ---

@pytest.fixture(scope="module", autouse=True)
def setup_test_env_e2e():
    """Set up environment variables for E2E testing and reset after."""
    original_env_mode = os.environ.get("ENV_MODE")
    original_test_mode = os.environ.get("TEST_MODE")
    original_analytics_enabled = os.environ.get("ANALYTICS_ENABLED")
    original_outreach_enabled = os.environ.get("OUTREACH_ENABLED")
    original_dry_run_mode = os.environ.get("DRY_RUN_MODE")
    
    os.environ["ENV_MODE"] = "test"
    os.environ["TEST_MODE"] = "True"
    os.environ["ANALYTICS_ENABLED"] = "True" # Enable analytics for full test
    os.environ["OUTREACH_ENABLED"] = "False" # Disable real outreach
    os.environ["DRY_RUN_MODE"] = "True" # Force outreach dry run
    
    settings._rebuild() # Re-instantiate settings to pick up test environment variables
    outreach_settings._rebuild()
    
    yield
    
    # Clean up environment variables
    if original_env_mode: os.environ["ENV_MODE"] = original_env_mode
    else: del os.environ["ENV_MODE"]
    if original_test_mode: os.environ["TEST_MODE"] = original_test_mode
    else: del os.environ["TEST_MODE"]
    if original_analytics_enabled: os.environ["ANALYTICS_ENABLED"] = original_analytics_enabled
    else: del os.environ["ANALYTICS_ENABLED"]
    if original_outreach_enabled: os.environ["OUTREACH_ENABLED"] = original_outreach_enabled
    else: del os.environ["OUTREACH_ENABLED"]
    if original_dry_run_mode: os.environ["DRY_RUN_MODE"] = original_dry_run_mode
    else: del os.environ["DRY_RUN_MODE"]

    settings._rebuild() # Revert settings
    outreach_settings._rebuild()


@pytest.fixture(autouse=True)
def clean_db(tmp_path):
    """Cleans up the test SQLite DB for each test."""
    test_db_path = tmp_path / "test_orchestrator.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Patch SQLStore to use the temporary DB
    with patch('orchestrator.src.memory.sql_store.SQLStore.__init__', autospec=True) as mock_sql_init:
        mock_sql_init.side_effect = lambda self, db_url=None: SQLStore.__init__(self, db_url=f"sqlite:///{test_db_path}")
        yield test_db_path

@pytest.fixture
def mock_catalog_json(tmp_path):
    """Creates a temporary products.json for testing."""
    test_catalog_data = [
        {"id": "prod_x", "name": "Product X", "price": 10, "funnel_stage": "entry", "primary_entry_offer": True, "checkout_url": "link_x"},
        {"id": "prod_y", "name": "Product Y", "price": 20, "funnel_stage": "growth", "upsell_to": ["prod_z"], "checkout_url": "link_y"},
    ]
    catalog_path = tmp_path / "products.json"
    with open(catalog_path, "w") as f:
        json.dump(test_catalog_data, f)
    
    # Mock open to return this temporary file
    with patch('orchestrator.src.core.api.open', MagicMock(
        side_effect=lambda f, mode='r', **kwargs: open(catalog_path, mode, **kwargs) if 'products.json' in f else open(f, mode, **kwargs)
    )), patch('orchestrator.src.core.monetization.engine.open', MagicMock(
        side_effect=lambda f, mode='r', **kwargs: open(catalog_path, mode, **kwargs) if 'products.json' in f else open(f, mode, **kwargs)
    )):
        yield catalog_path

# --- Self-Test Script ---
# This script will run a series of critical checks
# It does NOT spin up the full FastAPI app but checks core components directly

def test_db_connectivity(clean_db):
    """Verify that SQLStore can connect to the test database."""
    sql = SQLStore()
    session = sql.Session()
    assert session is not None
    session.close()

def test_product_catalog_loading(mock_catalog_json):
    """Verify that the product catalog can be loaded by MonetizationEngine."""
    engine = MonetizationEngine()
    assert len(engine._products) == 2
    assert any(p["id"] == "prod_x" for p in engine._products)

def test_outreach_settings_load():
    """Verify that outreach settings load correctly."""
    assert outreach_settings.OUTREACH_ENABLED == False
    assert outreach_settings.DRY_RUN_MODE == True
    assert outreach_settings.OUTREACH_TEST_RECIPIENT == "test@example.com"

@pytest.mark.asyncio
async def test_arq_pool_creation():
    """Verify ARQ pool can be created using test Redis settings."""
    from arq import create_pool
    from arq.connections import RedisSettings
    
    # Mock redis connection for testing
    with patch('arq.connections.Redis.from_url', return_value=MagicMock()):
        redis = RedisSettings.from_dsn(outreach_settings.REDIS_URL)
        pool = await create_pool(redis)
        assert pool is not None
        await pool.close()

def test_stripe_config_load():
    """Verify Stripe test config loads correctly."""
    assert settings.STRIPE_TEST_MODE == True
    assert settings.STRIPE_API_KEY == "sk_test_mock_key"
    assert settings.STRIPE_PUBLISHABLE_KEY == "pk_test_mock_key"
    assert settings.STRIPE_WEBHOOK_SECRET == "whsec_test_mock_secret"

# This script can be run directly as a simple self-test
if __name__ == "__main__":
    print("Running Monetization Stack Self-Test...")
    pytest.main([__file__])
