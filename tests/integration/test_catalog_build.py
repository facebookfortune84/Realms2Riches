import pytest
import os
import json
from unittest.mock import patch, MagicMock
from scripts import build_catalog

@pytest.fixture
def clean_catalog_dir(tmp_path):
    """Ensures a clean state for the catalog directory before each test."""
    catalog_path = tmp_path / "products.json"
    if os.path.exists(catalog_path):
        os.remove(catalog_path)
    # Patch the script's catalog path to use the temporary directory
    original_catalog_path = build_catalog.output_path
    build_catalog.output_path = str(catalog_path)
    yield catalog_path
    if os.path.exists(catalog_path):
        os.remove(catalog_path)
    build_catalog.output_path = original_catalog_path # Revert path

def test_build_catalog_generates_18_products(clean_catalog_dir):
    """
    Test that build_catalog.py correctly generates products.json with 18 products.
    """
    # Run the script
    build_catalog.products # Accessing it will run the module-level code
    
    # Verify the output file exists
    assert os.path.exists(clean_catalog_dir)
    
    # Verify content
    with open(clean_catalog_dir, "r") as f:
        products = json.load(f)
    
    assert len(products) == 18, f"Expected 18 products, but found {len(products)}"
    
    # Basic structure check for one product
    first_product = products[0]
    assert "id" in first_product
    assert "name" in first_product
    assert "price" in first_product
    assert "funnel_stage" in first_product

def test_build_catalog_is_idempotent(clean_catalog_dir):
    """
    Test that running build_catalog multiple times does not change the result.
    """
    # First run
    build_catalog.products
    
    with open(clean_catalog_dir, "r") as f:
        first_run_products = json.load(f)
    
    # Second run
    build_catalog.products
    
    with open(clean_catalog_dir, "r") as f:
        second_run_products = json.load(f)
    
    assert first_run_products == second_run_products
