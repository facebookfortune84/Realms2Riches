"""
Sync Stripe products/prices/payment links from data/catalog/products.json.
"""
import json
import logging
import os

import stripe
from dotenv import load_dotenv
from stripe import StripeError

# Load .env.prod for the live key
load_dotenv(".env.prod")
stripe.api_key = os.getenv("STRIPE_API_KEY")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("STRIPE_SYNC")


def get_existing_products():
    """Fetches all active products from Stripe to ensure idempotency."""
    try:
        products = stripe.Product.list(active=True, limit=100)
        return {p.name: p.id for p in products}
    except Exception as e:
        logger.error(f"Failed to fetch existing Stripe products: {e}")
        return {}


def create_products():
    # Load from catalog
    catalog_path = "data/catalog/products.json"
    if not os.path.exists(catalog_path):
        logger.error(
            f"Catalog file {catalog_path} not found. Run scripts/build_catalog.py first."
        )
        return

    with open(catalog_path, "r") as f:
        catalog = json.load(f)

    existing_stripe_products = get_existing_products()

    results = []
    updated_catalog = False

    for p in catalog:
        product_name = p["name"]
        product_id = p["id"]

        # Check if product needs creation (placeholder link) or if we want to force sync
        is_placeholder = "test_link" in p.get("checkout_url", "")

        if product_name in existing_stripe_products:
            logger.info(
                f"Product '{product_name}' already exists in Stripe (ID: {existing_stripe_products[product_name]})."
            )
            continue

        if not is_placeholder:
            logger.info(f"Skipping '{product_name}': already has a custom/live link.")
            continue

        logger.info(f"Creating Stripe Product for: {product_name}...")
        try:
            # 1. Create Product
            stripe_product = stripe.Product.create(
                name=product_name,
                description=p.get("description", ""),
                metadata={"internal_id": product_id},
            )

            # 2. Create Price
            amount_cents = int(p["price"] * 100)
            price_args = {
                "product": stripe_product.id,
                "unit_amount": amount_cents,
                "currency": "usd",
            }
            if p.get("interval") and p["interval"] != "once":
                price_args["recurring"] = {"interval": p["interval"]}

            stripe_price = stripe.Price.create(**price_args)

            # 3. Create Payment Link
            pay_link = stripe.PaymentLink.create(
                line_items=[{"price": stripe_price.id, "quantity": 1}]
            )

            # Update catalog entry
            p["checkout_url"] = pay_link.url
            updated_catalog = True

            results.append(
                {
                    "id": product_id,
                    "stripe_product_id": stripe_product.id,
                    "stripe_price_id": stripe_price.id,
                    "payment_link": pay_link.url,
                }
            )
            logger.info(f"Successfully synced '{product_name}' -> {pay_link.url}")

        except StripeError as e:
            logger.error(
                f"Stripe API error for '{product_name}': {e.user_message if hasattr(e, 'user_message') else str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error for '{product_name}': {e}")

    if updated_catalog:
        with open(catalog_path, "w") as f:
            json.dump(catalog, f, indent=2)
        logger.info(f"Updated {catalog_path} with new Stripe links.")

    if results:
        audit_path = "data/catalog/stripe_sync_audit.json"
        with open(audit_path, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Sync audit saved to {audit_path}")
    else:
        logger.info("Stripe sync complete. No new products created.")


if __name__ == "__main__":
    create_products()
