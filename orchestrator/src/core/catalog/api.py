from typing import List, Optional
from orchestrator.src.core.catalog.models import ProductModel, PriceModel, ProductSchema, PriceSchema
from orchestrator.src.memory.sql_store import SQLStore
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class CatalogAPI:
    def __init__(self):
        self.store = SQLStore()
    
    def get_products(self) -> List[ProductSchema]:
        """Fetch and merge all products from modular slots and the database."""
        import json
        import glob
        import os
        
        products_map = {}
        slot_path = "data/store/slots/*.json"
        
        # 1. Load from Database (Primary source for seeded products)
        session = self.store.Session()
        try:
            db_products = session.query(ProductModel).all()
            for p in db_products:
                products_map[p.id] = ProductSchema(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    category=p.category,
                    image_url=p.image_url,
                    checkout_url=p.checkout_url,
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
        except Exception as e:
            logger.error(f"Database Catalog Fetch Error: {e}")
        finally:
            session.close()

        # 2. Merge from Slots (JSON files)
        try:
            for slot_file in glob.glob(slot_path):
                try:
                    with open(slot_file, 'r') as f:
                        data = json.load(f)
                        products_in_file = data if isinstance(data, list) else [data]
                        
                        for p in products_in_file:
                            pid = p.get("id")
                            if not pid: continue
                            
                            # NORMALIZATION
                            if "prices" not in p and "price" in p:
                                p["prices"] = [{
                                    "product_id": pid,
                                    "price": p.get("price"),
                                    "currency": p.get("currency", "usd"),
                                    "interval": p.get("interval", "mo"),
                                    "stripe_price_id": p.get("stripe_price_id")
                                }]
                            if "category" not in p: p["category"] = "General"
                            
                            # Add to map if not present (don't override DB products which have better URLs)
                            if pid not in products_map and p.get("price") is not None:
                                products_map[pid] = ProductSchema(**p)
                except Exception as e:
                    logger.error(f"Skipping corrupt slot file {slot_file}: {e}")
        except Exception as e:
            logger.error(f"Catalog Expansion Error: {e}")

        return list(products_map.values())

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
                image_url=p.image_url,
                checkout_url=p.checkout_url,
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
