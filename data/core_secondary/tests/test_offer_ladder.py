import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

from orchestrator.src.core.monetization.engine import MonetizationEngine

def test_catalog_load_and_metadata():
    engine = MonetizationEngine()
    products = engine._products
    
    assert len(products) == 18, f"Expected 18 products, found {len(products)}"
    
    for p in products:
        assert "funnel_stage" in p, f"Product {p['id']} missing funnel_stage"
        assert "upsell_to" in p, f"Product {p['id']} missing upsell_to"
        assert "cross_sell_with" in p, f"Product {p['id']} missing cross_sell_with"

def test_entry_offers():
    engine = MonetizationEngine()
    entries = engine.get_entry_offers()
    
    assert len(entries) > 0
    ids = [p["id"] for p in entries]
    assert "jarvis_basic" in ids
    assert "business_consultation" in ids

def test_recommendations():
    engine = MonetizationEngine()
    recs = engine.get_recommendations("website_basic")
    
    assert "upsells" in recs
    assert "cross_sells" in recs
    
    upsell_ids = [p["id"] for p in recs["upsells"]]
    assert "website_advanced" in upsell_ids
    
    cross_ids = [p["id"] for p in recs["cross_sells"]]
    assert "brand_kit" in cross_ids

def test_by_stage():
    engine = MonetizationEngine()
    growth_products = engine.get_products_by_stage("growth")
    
    assert len(growth_products) > 0
    for p in growth_products:
        assert p["funnel_stage"] == "growth"

if __name__ == "__main__":
    # Manual run support
    try:
        test_catalog_load_and_metadata()
        test_entry_offers()
        test_recommendations()
        test_by_stage()
        print("✅ Offer Ladder Tests Passed.")
    except Exception as e:
        print(f"❌ Tests Failed: {e}")
        sys.exit(1)
