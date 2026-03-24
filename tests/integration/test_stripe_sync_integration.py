import builtins
import json
from unittest.mock import MagicMock, patch

import pytest
from stripe import StripeError

from scripts import create_new_stripe_products as stripe_script
from tests.mocks.mock_stripe import MockStripe, MockStripeProduct

_real_open = builtins.open


def _script_open_side_effect(catalog_file, audit_file):
    """Redirect script file opens to temp paths (avoids patching builtins.open + recursion)."""

    def _side_effect(path, mode="r", *args, **kwargs):
        sp = str(path)
        if "products.json" in sp:
            return _real_open(catalog_file, mode, *args, **kwargs)
        if "stripe_sync_audit" in sp:
            return _real_open(audit_file, mode, *args, **kwargs)
        return MagicMock()

    return _side_effect


@pytest.fixture
def mock_stripe_client():
    """Fixture to provide a clean mock Stripe client for each test."""
    mock_stripe = MockStripe()
    mock_stripe.products = []
    mock_stripe.prices = []
    mock_stripe.payment_links = []
    with (
        patch("stripe.Product", mock_stripe.Product),
        patch("stripe.Price", mock_stripe.Price),
        patch("stripe.PaymentLink", mock_stripe.PaymentLink),
        patch("stripe.api_key", "sk_test_mock_key"),
    ):
        yield mock_stripe


@pytest.fixture
def mock_catalog_file_for_stripe_sync(tmp_path):
    """Creates a temporary products.json for testing Stripe sync."""
    test_catalog_data = [
        {
            "id": "prod_a",
            "name": "Product A",
            "description": "Desc A",
            "price": 100,
            "interval": "once",
            "checkout_url": "https://buy.stripe.com/test_link_A",
            "funnel_stage": "entry",
        },
        {
            "id": "prod_b",
            "name": "Product B",
            "description": "Desc B",
            "price": 200,
            "interval": "month",
            "checkout_url": "https://buy.stripe.com/test_link_B",
            "funnel_stage": "growth",
        },
        {
            "id": "prod_c",
            "name": "Product C",
            "description": "Desc C",
            "price": 500,
            "interval": "once",
            "checkout_url": "https://real.stripe.com/prod_c_link",
            "funnel_stage": "entry",
        },
    ]
    catalog_path = tmp_path / "products.json"
    with _real_open(catalog_path, "w") as f:
        json.dump(test_catalog_data, f)
    return catalog_path


@patch("scripts.create_new_stripe_products.os.path.exists", return_value=True)
def test_stripe_sync_creates_products_and_updates_catalog(
    mock_exists, mock_stripe_client, mock_catalog_file_for_stripe_sync
):
    """
    Test that create_new_stripe_products.py correctly creates new Stripe products
    and updates the catalog with real Stripe links.
    """
    audit_file = mock_catalog_file_for_stripe_sync.parent / "stripe_sync_audit.json"
    with patch(
        "scripts.create_new_stripe_products.open",
        MagicMock(
            side_effect=_script_open_side_effect(
                mock_catalog_file_for_stripe_sync, audit_file
            )
        ),
    ):
        with _real_open(mock_catalog_file_for_stripe_sync, "r") as f:
            initial_catalog = json.load(f)
        assert "test_link" in initial_catalog[0]["checkout_url"]

        stripe_script.create_products()

    assert len(mock_stripe_client.products) == 2
    assert len(mock_stripe_client.prices) == 2
    assert len(mock_stripe_client.payment_links) == 2

    prod_a_stripe = next(p for p in mock_stripe_client.products if p.name == "Product A")
    assert prod_a_stripe.name == "Product A"
    prod_b_stripe = next(p for p in mock_stripe_client.products if p.name == "Product B")
    assert prod_b_stripe.name == "Product B"

    with _real_open(mock_catalog_file_for_stripe_sync, "r") as f:
        updated_catalog = json.load(f)

    prod_a_updated = next(p for p in updated_catalog if p["id"] == "prod_a")
    assert "test_link_1" in prod_a_updated["checkout_url"]

    prod_c_updated = next(p for p in updated_catalog if p["id"] == "prod_c")
    assert prod_c_updated["checkout_url"] == "https://real.stripe.com/prod_c_link"


@patch("scripts.create_new_stripe_products.os.path.exists", return_value=True)
def test_stripe_sync_is_idempotent(
    mock_exists, mock_stripe_client, mock_catalog_file_for_stripe_sync
):
    """Test that re-running the script does not create duplicate products in Stripe."""
    audit_file = mock_catalog_file_for_stripe_sync.parent / "stripe_sync_audit.json"
    with patch(
        "scripts.create_new_stripe_products.open",
        MagicMock(
            side_effect=_script_open_side_effect(
                mock_catalog_file_for_stripe_sync, audit_file
            )
        ),
    ):
        stripe_script.create_products()
        assert len(mock_stripe_client.products) == 2

        stripe_script.create_products()
        assert len(mock_stripe_client.products) == 2
        assert len(mock_stripe_client.prices) == 2
        assert len(mock_stripe_client.payment_links) == 2

        with _real_open(mock_catalog_file_for_stripe_sync, "r") as f:
            updated_catalog = json.load(f)
        prod_a_updated = next(p for p in updated_catalog if p["id"] == "prod_a")
        assert "test_link_1" in prod_a_updated["checkout_url"]


@patch("scripts.create_new_stripe_products.os.path.exists", return_value=True)
def test_stripe_sync_handles_api_errors(
    mock_exists, mock_stripe_client, mock_catalog_file_for_stripe_sync
):
    """Test that the script gracefully handles Stripe API errors and logs them."""

    def mock_product_create_fail(**kwargs):
        if kwargs["name"] == "Product A":
            raise StripeError("API Error for Product A during creation")
        return MockStripeProduct(
            id="prod_b_id",
            name=kwargs["name"],
            description=kwargs["description"],
            metadata={},
        )

    audit_file = mock_catalog_file_for_stripe_sync.parent / "stripe_sync_audit.json"
    with patch(
        "scripts.create_new_stripe_products.open",
        MagicMock(
            side_effect=_script_open_side_effect(
                mock_catalog_file_for_stripe_sync, audit_file
            )
        ),
    ), patch("stripe.Product.create", side_effect=mock_product_create_fail):
        stripe_script.create_products()

    assert len(mock_stripe_client.products) == 1
    assert mock_stripe_client.products[0].name == "Product B"

    with _real_open(mock_catalog_file_for_stripe_sync, "r") as f:
        updated_catalog = json.load(f)
    prod_a_updated = next(p for p in updated_catalog if p["id"] == "prod_a")
    assert "test_link_A" in prod_a_updated["checkout_url"]
