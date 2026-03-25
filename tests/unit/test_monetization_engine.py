import pytest
import json
from unittest.mock import patch
from orchestrator.src.core.monetization.engine import MonetizationEngine

@pytest.fixture
def mock_catalog_file(tmp_path):
    """Creates a temporary products.json for testing."""
    test_catalog_data = [
        {
            "id": "prod_a", "name": "Product A", "price": 100, "interval": "once", 
            "checkout_url": "http://checkout.com/a", "funnel_stage": "entry", "primary_entry_offer": True,
            "upsell_to": ["prod_b"], "cross_sell_with": []
        },
        {
            "id": "prod_b", "name": "Product B", "price": 200, "interval": "month", 
            "checkout_url": "http://checkout.com/b", "funnel_stage": "growth", "primary_entry_offer": False,
            "upsell_to": [], "cross_sell_with": ["prod_c"]
        },
        {
            "id": "prod_c", "name": "Product C", "price": 50, "interval": "once", 
            "checkout_url": "http://checkout.com/c", "funnel_stage": "entry", "primary_entry_offer": False,
            "upsell_to": [], "cross_sell_with": []
        }
    ]
    catalog_path = tmp_path / "products.json"
    with open(catalog_path, "w") as f:
        json.dump(test_catalog_data, f)
    
    # Temporarily point the engine to this mock catalog file
    original_path = MonetizationEngine.__init__.__globals__['open']
    MonetizationEngine.__init__.__globals__['open'] = lambda *args, **kwargs: open(catalog_path, *args, **kwargs)
    yield catalog_path
    MonetizationEngine.__init__.__globals__['open'] = original_path

def test_monetization_engine_loads_catalog(mock_catalog_file):
    """Test that the engine loads products from the catalog file."""
    engine = MonetizationEngine()
    assert len(engine._products) == 3
    assert any(p["id"] == "prod_a" for p in engine._products)

def test_monetization_engine_get_products_by_stage(mock_catalog_file):
    """Test filtering products by funnel stage."""
    engine = MonetizationEngine()
    entry_products = engine.get_products_by_stage("entry")
    assert len(entry_products) == 2
    assert all(p["funnel_stage"] == "entry" for p in entry_products)

def test_monetization_engine_get_entry_offers(mock_catalog_file):
    """Test retrieving only primary entry offers."""
    engine = MonetizationEngine()
    entry_offers = engine.get_entry_offers()
    assert len(entry_offers) == 1
    assert entry_offers[0]["id"] == "prod_a"

def test_monetization_engine_get_recommendations(mock_catalog_file):
    """Test retrieving upsell and cross-sell recommendations."""
    engine = MonetizationEngine()
    recs = engine.get_recommendations("prod_a")
    assert len(recs["upsells"]) == 1
    assert recs["upsells"][0]["id"] == "prod_b"
    assert len(recs["cross_sells"]) == 0

    recs_b = engine.get_recommendations("prod_b")
    assert len(recs_b["cross_sells"]) == 1
    assert recs_b["cross_sells"][0]["id"] == "prod_c"

    recs_non_existent = engine.get_recommendations("non_existent_prod")
    assert len(recs_non_existent["upsells"]) == 0
    assert len(recs_non_existent["cross_sells"]) == 0

@patch('orchestrator.src.core.orchestrator.Orchestrator')
@patch('orchestrator.src.core.monetization.engine.STRIPE_MONETIZATION', {"prod_a": "http://checkout.com/a"})
def test_monetization_engine_streams_init(mock_orchestrator, mock_catalog_file):
    """Test that streams are initialized with correct links."""
    engine = MonetizationEngine()
    # Find a stream that uses STRIPE_MONETIZATION, e.g., APISaaSBillingStream
    api_saas_stream = next((s for s in engine.streams if s.name == "APISaaSBilling"), None)
    assert api_saas_stream is not None
    assert api_saas_stream.links[0] == "http://checkout.com/a"
