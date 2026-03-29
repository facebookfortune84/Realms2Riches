import pytest
import os
import json
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

# Import the script to be tested
from scripts import build_catalog

@pytest.fixture
def clean_catalog_dir():
    """Ensures a clean state for the catalog directory before each test."""
    catalog_path = "data/catalog/products.json"
    if os.path.exists(catalog_path):
        os.remove(catalog_path)
    yield
    if os.path.exists(catalog_path):
        os.remove(catalog_path)

def test_build_catalog_generates_18_products(clean_catalog_dir):
    """
    Test that build_catalog.py correctly generates products.json with 18 products.
    """
    # Run the script
    build_catalog.products # Accessing it will run the module-level code
    
    # Verify the output file exists
    catalog_file = "data/catalog/products.json"
    assert os.path.exists(catalog_file)
    
    # Verify content
    with open(catalog_file, "r") as f:
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
    
    with open("data/catalog/products.json", "r") as f:
        first_run_products = json.load(f)
    
    # Second run
    build_catalog.products
    
    with open("data/catalog/products.json", "r") as f:
        second_run_products = json.load(f)
    
    assert first_run_products == second_run_products
