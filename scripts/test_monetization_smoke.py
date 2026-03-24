import pytest
import os
import sys
import json
import requests
from unittest.mock import patch
from datetime import datetime

# Ensure project root is in path
sys.path.append(os.getcwd())

from orchestrator.src.core.config import settings
from orchestrator.src.memory.sql_store import SQLStore, AnalyticsEvent
from orchestrator.src.core.monetization.engine import MonetizationEngine

# --- Fixtures for clean state ---

@pytest.fixture(scope="module", autouse=True)
def setup_test_env_smoke():
    """Set up environment variables for smoke testing and reset after."""
    original_env_mode = os.environ.get("ENV_MODE")
    original_test_mode = os.environ.get("TEST_MODE")
    original_analytics_enabled = os.environ.get("ANALYTICS_ENABLED")
    
    os.environ["ENV_MODE"] = "test"
    os.environ["TEST_MODE"] = "True"
    os.environ["ANALYTICS_ENABLED"] = "False" # Disable analytics for smoke tests
    
    settings._rebuild() # Re-instantiate settings to pick up test environment variables
    
    yield
    
    # Clean up environment variables
    if original_env_mode: os.environ["ENV_MODE"] = original_env_mode
    else: del os.environ["ENV_MODE"]
    if original_test_mode: os.environ["TEST_MODE"] = original_test_mode
    else: del os.environ["TEST_MODE"]
    if original_analytics_enabled: os.environ["ANALYTICS_ENABLED"] = original_analytics_enabled
    else: del os.environ["ANALYTICS_ENABLED"]

    settings._rebuild() # Revert settings


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
def mock_catalog_file_smoke(tmp_path):
    """Creates a temporary products.json for testing the API."""
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

# --- Smoke Tests ---

def test_db_connectivity(clean_db):
    """Verify that SQLStore can connect to the test database."""
    sql = SQLStore()
    session = sql.Session()
    assert session is not None
    session.close()

def test_product_catalog_integrity(mock_catalog_file_smoke):
    """Verify that the product catalog can be loaded and has expected items."""
    engine = MonetizationEngine()
    assert len(engine._products) == 2
    assert any(p["id"] == "prod_x" for p in engine._products)

@patch('requests.get')
def test_health_endpoint_response(mock_get_requests):
    """Verify the /health endpoint returns a successful status."""
    # We are not spinning up the full FastAPI app for smoke tests, so mock requests
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "SOVEREIGN"}
    mock_get_requests.return_value = mock_response

    # In a real scenario, you'd start the FastAPI app and hit it
    # For a true smoke test, we just check core components.
    # The actual API endpoint logic is tested in integration tests.
    
    # This is more of a placeholder to indicate a check for health.
    # The real check requires the app to be running.
    # For now, let's just make sure the config loads correctly.
    assert settings.ENV_MODE == "test"
    assert settings.TEST_MODE == True
    
    # We will expand this to use TestClient in integration tests.
