import pytest
import json
from stripe import StripeError
from unittest.mock import patch, MagicMock
from scripts import create_new_stripe_products as stripe_script
from tests.mocks.mock_stripe import MockStripe, MockStripeProduct

@pytest.fixture
def mock_stripe_client():
    """Fixture to provide a clean mock Stripe client for each test."""
    mock_stripe = MockStripe()
    mock_stripe.products = []
    mock_stripe.prices = []
    mock_stripe.payment_links = []
    with (patch('stripe.Product', mock_stripe.Product), 
         patch('stripe.Price', mock_stripe.Price), 
         patch('stripe.PaymentLink', mock_stripe.PaymentLink), 
         patch('stripe.api_key', "sk_test_mock_key")):
        yield mock_stripe

@pytest.fixture
def mock_catalog_file(tmp_path):
    """Creates a temporary products.json for testing."""
    test_catalog_data = [
        {
            "id": "prod_a", "name": "Product A", "description": "Desc A", "price": 100, "interval": "once", 
            "checkout_url": "https://buy.stripe.com/test_link_A", "funnel_stage": "entry"
        },
        {
            "id": "prod_b", "name": "Product B", "description": "Desc B", "price": 200, "interval": "month", 
            "checkout_url": "https://buy.stripe.com/test_link_B", "funnel_stage": "growth"
        },
        {
            "id": "prod_c", "name": "Product C", "description": "Desc C", "price": 500, "interval": "once", 
            "checkout_url": "https://real.stripe.com/prod_c_link", "funnel_stage": "entry" # Already has a real link
        }
    ]
    catalog_path = tmp_path / "products.json"
    with open(catalog_path, "w") as f:
        json.dump(test_catalog_data, f)
    return catalog_path

@patch('scripts.create_new_stripe_products.os.path.exists', return_value=True)
def test_create_products_creates_new_products(mock_exists, mock_stripe_client, mock_catalog_file):
    """Test that the script creates new Stripe products for placeholder links."""
    with patch('scripts.create_new_stripe_products.open', MagicMock(
        side_effect=lambda f, mode='r', **kwargs: open(mock_catalog_file, mode, **kwargs) if 'products.json' in str(f) else MagicMock()
    )):
        stripe_script.create_products()

    assert len(mock_stripe_client.products) == 2 # prod_a, prod_b
    assert len(mock_stripe_client.prices) == 2
    assert len(mock_stripe_client.payment_links) == 2

    # Verify prod_a
    prod_a_stripe = next(p for p in mock_stripe_client.products if p.name == "Product A")
    assert prod_a_stripe.description == "Desc A"
    assert prod_a_stripe.metadata["internal_id"] == "prod_a"

    # Verify updated catalog file
    with open(mock_catalog_file, "r") as f:
        updated_catalog = json.load(f)
    
    prod_a_updated = next(p for p in updated_catalog if p["id"] == "prod_a")
    assert "test_link_1" in prod_a_updated["checkout_url"] # Mock link format

@patch('scripts.create_new_stripe_products.os.path.exists', return_value=True)
def test_create_products_is_idempotent(mock_exists, mock_stripe_client, mock_catalog_file):
    """Test that re-running the script does not create duplicate products."""
    with patch('scripts.create_new_stripe_products.open', MagicMock(
        side_effect=lambda f, mode='r', **kwargs: open(mock_catalog_file, mode, **kwargs) if 'products.json' in str(f) else MagicMock()
    )):
        # First run
        stripe_script.create_products()
        assert len(mock_stripe_client.products) == 2
        
        # Second run
        stripe_script.create_products()
        assert len(mock_stripe_client.products) == 2 # Should not create new products
        assert len(mock_stripe_client.prices) == 2
        assert len(mock_stripe_client.payment_links) == 2

@patch('scripts.create_new_stripe_products.os.path.exists', return_value=True)
def test_create_products_handles_api_errors(mock_exists, mock_stripe_client, mock_catalog_file):
    """Test that the script gracefully handles Stripe API errors."""
    def mock_product_create(**kwargs):
        if kwargs['name'] == "Product A":
            raise StripeError("API Error for Product A")
        return MockStripeProduct(id="prod_b_id", name=kwargs['name'], description=kwargs['description'], metadata={})
    
    with patch('scripts.create_new_stripe_products.open', MagicMock(
        side_effect=lambda f, mode='r', **kwargs: open(mock_catalog_file, mode, **kwargs) if 'products.json' in str(f) else MagicMock()
    )), patch('stripe.Product.create', side_effect=mock_product_create):
        stripe_script.create_products()

    assert len(mock_stripe_client.products) == 1 # Only Product B should be created
    # Ensure error was logged (can check logging output, but for now, just count created)
