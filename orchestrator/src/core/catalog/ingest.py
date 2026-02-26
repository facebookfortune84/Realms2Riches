import pandas as pd
from sqlalchemy.orm import Session
from orchestrator.src.memory.sql_store import SQLStore
from orchestrator.src.core.catalog.models import ProductModel, PriceModel
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

def seed_catalog(products_csv_path="data/catalog/products.csv", prices_csv_path="data/catalog/prices.csv"):
    logger.info("Starting product catalog seeding...")
    
    store = SQLStore()
    session = store.Session()

    try:
        # 0. Clear Existing Data (Purge for clean state)
        session.query(PriceModel).delete()
        session.query(ProductModel).delete()
        session.commit()

        # Load CSVs
        products_df = pd.read_csv(products_csv_path)
        prices_df = pd.read_csv(prices_csv_path)

        # 1. Seed Products
        seeded_product_ids = set()
        for _, row in products_df.iterrows():
            product_id = str(row['id']).strip()
            seeded_product_ids.add(product_id)
            
            new_product = ProductModel(
                id=product_id,
                name=row['name'],
                description=row['description'],
                category=row['category'],
                image_url=row.get('image_url')
            )
            session.add(new_product)
        
        session.flush()

        # 2. Seed Prices
        for _, row in prices_df.iterrows():
            pid = str(row['product_id']).strip()
            if pid not in seeded_product_ids:
                logger.warning(f"Skipping price for unknown product: '{pid}' (Seeded: {seeded_product_ids})")
                continue

            new_price = PriceModel(
                product_id=row['product_id'],
                price=float(row['price']),
                currency=row['currency'],
                interval=row['interval'],
                stripe_price_id=row.get('stripe_price_id')
            )
            session.add(new_price)
            
        session.commit()
        logger.info("Product catalog seeding completed successfully.")

    except Exception as e:
        session.rollback()
        logger.error(f"Failed to seed catalog: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed_catalog()
