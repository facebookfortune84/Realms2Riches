import sys
import os
sys.path.append(os.getcwd())

import pytest
import os
import json
import uuid
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from orchestrator.src.core.api import app
from orchestrator.src.memory.sql_store import SQLStore, AnalyticsEvent, ProfitRecord
import orchestrator.src.core.config

# --- Fixtures for clean state ---

@pytest.fixture(scope="module")
def test_client():
    """Provides a TestClient for the FastAPI app, ensuring settings are configured for testing."""
    original_env_vars = {k: os.environ[k] for k in os.environ if k.startswith("TEST_") or k.startswith("STRIPE_") or k.startswith("ANALYTICS_") or k == "ENV_MODE"} # Save original relevant env vars

    # Set test environment variables
    os.environ["ENV_MODE"] = "test"
    os.environ["TEST_MODE"] = "True"
    os.environ["ANALYTICS_ENABLED"] = "False" # Default to false for these tests
    os.environ["STRIPE_TEST_MODE"] = "True"
    os.environ["STRIPE_API_KEY"] = "sk_test_mock_key"
    os.environ["STRIPE_PUBLISHABLE_KEY"] = "pk_test_mock_key"
    os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test_mock_secret"
    
    global settings
    settings = orchestrator.src.core.config.settings
    import importlib
    importlib.reload(orchestrator.src.core.config)
    settings = orchestrator.src.core.config.settings

    with TestClient(app) as client:
        yield client

    # Clean up environment variables and reload settings
    for k in [k for k in os.environ if k.startswith("TEST_") or k.startswith("STRIPE_") or k.startswith("ANALYTICS_") or k == "ENV_MODE"]:
        if k in original_env_vars:
            os.environ[k] = original_env_vars[k]
        else:
            del os.environ[k]
    
    importlib.reload(orchestrator.src.core.config)
    settings = orchestrator.src.core.config.settings


@pytest.fixture(autouse=True)
def clean_db_and_catalog(tmp_path):
    """Cleans up the test SQLite DB and ensures a fresh catalog for each test."""
    test_db_path = tmp_path / "test_orchestrator.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    real_init = SQLStore.__init__

    def _patched_init(self, db_url=None, *args, **kwargs):
        return real_init(self, db_url=f"sqlite:///{test_db_path}", *args, **kwargs)

    with patch.object(SQLStore, "__init__", _patched_init):
        yield test_db_path

@pytest.fixture
def mock_catalog_json(tmp_path):
    """Creates a temporary products.json for testing the API."""
    test_catalog_data = [
        {"id": "prod_x", "name": "Product X", "price": 10, "funnel_stage": "entry", "primary_entry_offer": True, "checkout_url": "link_x"},
        {"id": "prod_y", "name": "Product Y", "price": 20, "funnel_stage": "growth", "upsell_to": ["prod_z"], "checkout_url": "link_y"},
        {"id": "prod_z", "name": "Product Z", "price": 30, "funnel_stage": "scale", "cross_sell_with": ["prod_x"], "checkout_url": "link_z"},
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

# --- Tests ---

def test_get_products_all(test_client, mock_catalog_json):
    """Test fetching all products from the API."""
    response = test_client.get("/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 3
    assert any(p["id"] == "prod_x" for p in products)

def test_get_products_by_stage(test_client, mock_catalog_json):
    """Test fetching products filtered by funnel stage."""
    response = test_client.get("/products?stage=entry")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 1
    assert products[0]["id"] == "prod_x"

def test_get_products_entry_only(test_client, mock_catalog_json):
    """Test fetching only primary entry offers."""
    response = test_client.get("/products?entry_only=true")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 1
    assert products[0]["id"] == "prod_x"

def test_get_products_recommendations(test_client, mock_catalog_json):
    """Test fetching recommendations for a specific product."""
    response = test_client.get("/products?recommendations_for=prod_y")
    assert response.status_code == 200
    recs = response.json()
    assert len(recs["upsells"]) == 1
    assert recs["upsells"][0]["id"] == "prod_z"
    assert len(recs["cross_sells"]) == 0 # Based on mock data

def test_record_analytics_event_disabled(test_client, clean_db_and_catalog):
    """Test that analytics events are not recorded when ANALYTICS_ENABLED is False."""
    os.environ["ANALYTICS_ENABLED"] = "False"

    
    response = test_client.post("/api/v1/analytics/event", json={
        "event_type": "PRODUCT_VIEW", "product_id": "prod_test", "user_id": "user123"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "skipped"

    sql = SQLStore()
    session = sql.Session()
    assert session.query(AnalyticsEvent).filter_by(event_type="PRODUCT_VIEW").count() == 0
    session.close()

def test_record_analytics_event_enabled(test_client, clean_db_and_catalog):
    """Test that analytics events are recorded when ANALYTICS_ENABLED is True."""
    os.environ["ANALYTICS_ENABLED"] = "True"


    response = test_client.post("/api/v1/analytics/event", json={
        "event_type": "PRODUCT_VIEW", "product_id": "prod_test", "user_id": "user123"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "recorded"

    sql = SQLStore()
    session = sql.Session()
    assert session.query(AnalyticsEvent).filter_by(event_type="PRODUCT_VIEW").count() == 1
    event = session.query(AnalyticsEvent).filter_by(event_type="PRODUCT_VIEW").first()
    assert event.event_type == "PRODUCT_VIEW"
    assert event.product_id == "prod_test"
    session.close()

def test_stripe_webhook_analytics_event(test_client, clean_db_and_catalog):
    """Test that a CHECKOUT_COMPLETED event is recorded via webhook."""
    os.environ["ANALYTICS_ENABLED"] = "True"

    ev_id = f"evt_test_{uuid.uuid4().hex[:12]}"
    mock_event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "amount_total": 10000,
                "currency": "usd",
                "customer_details": {"email": "test@example.com"},
                "metadata": {"internal_id": "prod_x"}
            }
        },
        "id": ev_id,
    }
    
    # Mock stripe.Webhook.construct_event as it needs a real payload/signature
    with patch('stripe.Webhook.construct_event', return_value=mock_event):
        response = test_client.post(
            "/api/v1/monetization/webhook", 
            headers={"stripe-signature": "t=123,v1=abc"}, 
            json=mock_event
        )
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    sql = SQLStore()
    session = sql.Session()
    # Check ProfitRecord
    assert session.query(ProfitRecord).count() == 1
    # Check AnalyticsEvent
    assert session.query(AnalyticsEvent).filter_by(event_type="CHECKOUT_COMPLETED").count() == 1
    event = session.query(AnalyticsEvent).filter_by(event_type="CHECKOUT_COMPLETED").first()
    assert event.product_id == "prod_x"
    assert event.user_id == "test@example.com"
    session.close()