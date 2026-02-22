from typing import List, Optional
from orchestrator.src.core.catalog.models import ProductModel, PriceModel, ProductSchema, PriceSchema
from orchestrator.src.memory.sql_store import SQLStore
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class CatalogAPI:
    def __init__(self):
        self.store = SQLStore()
    
    def get_products(self) -> List[ProductSchema]:
        """Fetch all products dynamically from the modular slots directory."""
        import json
        import glob
        import os
        
        all_products = []
        slot_path = "data/store/slots/*.json"
        
        try:
            for slot_file in glob.glob(slot_path):
                try:
                    with open(slot_file, 'r') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            all_products.extend([ProductSchema(**p) if not isinstance(p, ProductSchema) else p for p in data])
                        else:
                            all_products.append(ProductSchema(**data) if not isinstance(data, ProductSchema) else data)
                except Exception as e:
                    logger.error(f"Skipping corrupt slot file {slot_file}: {e}")
            
            if all_products:
                return all_products
        except Exception as e:
            logger.error(f"Catalog Expansion Error: {e}")

        # Fallback to DB if directory scan fails
        session = self.store.Session()
        try:
            products = session.query(ProductModel).all()
            return [
                ProductSchema(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    category=p.category,
                    prices=[
                        PriceSchema(
                            product_id=pr.product_id,
                            price=pr.price,
                            currency=pr.currency,
                            interval=pr.interval,
                            stripe_price_id=pr.stripe_price_id
                        ) for pr in p.prices
                    ]
                ) for p in products
            ]
        finally:
            session.close()

    def get_product(self, product_id: str) -> Optional[ProductSchema]:
        session = self.store.Session()
        try:
            p = session.query(ProductModel).filter_by(id=product_id).first()
            if not p:
                return None
            return ProductSchema(
                id=p.id,
                name=p.name,
                description=p.description,
                category=p.category,
                prices=[
                    PriceSchema(
                        product_id=pr.product_id,
                        price=pr.price,
                        currency=pr.currency,
                        interval=pr.interval,
                        stripe_price_id=pr.stripe_price_id
                    ) for pr in p.prices
                ]
            )
        finally:
            session.close()

catalog_api = CatalogAPI()
