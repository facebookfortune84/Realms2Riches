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
        # Load CSVs
        products_df = pd.read_csv(products_csv_path)
        prices_df = pd.read_csv(prices_csv_path)

        # 1. Seed Products (Upsert Logic)
        for _, row in products_df.iterrows():
            product_id = row['id']
            existing_product = session.query(ProductModel).filter_by(id=product_id).first()
            
            if existing_product:
                existing_product.name = row['name']
                existing_product.description = row['description']
                existing_product.category = row['category']
            else:
                new_product = ProductModel(
                    id=product_id,
                    name=row['name'],
                    description=row['description'],
                    category=row['category']
                )
                session.add(new_product)

        # 2. Seed Prices (Delete existing & Re-insert for simplicity/idempotency)
        # Note: In production, consider upserting to preserve IDs if needed.
        # But prices often change or get replaced.
        session.query(PriceModel).delete()
        
        for _, row in prices_df.iterrows():
            # Check if product exists (FK constraint)
            if not session.query(ProductModel).filter_by(id=row['product_id']).first():
                logger.warning(f"Skipping price for unknown product: {row['product_id']}")
                continue

            new_price = PriceModel(
                product_id=row['product_id'],
                price=float(row['price']),
                currency=row['currency'],
                interval=row['interval']
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
