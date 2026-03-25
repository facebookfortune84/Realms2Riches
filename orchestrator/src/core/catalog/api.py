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
        
        all_products = []
        slot_path = "data/store/slots/*.json"
        
        try:
            for slot_file in glob.glob(slot_path):
                try:
                    with open(slot_file, 'r') as f:
                        data = json.load(f)
                        products_in_file = data if isinstance(data, list) else [data]
                        
                        for p in products_in_file:
                            # NORMALIZATION: Map flat 'price' to 'prices' list if needed
                            if "prices" not in p and "price" in p:
                                p["prices"] = [{
                                    "product_id": p.get("id"),
                                    "price": p.get("price"),
                                    "currency": p.get("currency", "usd"),
                                    "interval": p.get("interval", "mo"),
                                    "stripe_price_id": p.get("stripe_price_id")
                                }]
                            
                            # Ensure required 'category' exists
                            if "category" not in p:
                                p["category"] = "General"
                            
                            # Filter out null/corrupt entries
                            if p.get("id") and p.get("price") is not None:
                                all_products.append(ProductSchema(**p))
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

    def create_product(self, product: ProductSchema) -> bool:
        """Upsert a product and its prices into the database."""
        session = self.store.Session()
        try:
            # 1. Upsert Product
            db_product = session.query(ProductModel).filter_by(id=product.id).first()
            if not db_product:
                db_product = ProductModel(
                    id=product.id,
                    name=product.name,
                    description=product.description,
                    category=product.category
                )
                session.add(db_product)
            else:
                db_product.name = product.name
                db_product.description = product.description
                db_product.category = product.category
            
            session.flush()

            # 2. Upsert Prices
            for price in product.prices:
                db_price = session.query(PriceModel).filter_by(
                    product_id=product.id, 
                    price=price.price, 
                    currency=price.currency
                ).first()
                
                if not db_price:
                    db_price = PriceModel(
                        product_id=product.id,
                        price=price.price,
                        currency=price.currency,
                        interval=price.interval,
                        stripe_price_id=price.stripe_price_id
                    )
                    session.add(db_price)
                else:
                    db_price.interval = price.interval
                    db_price.stripe_price_id = price.stripe_price_id
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Catalog Create Error: {e}")
            return False
        finally:
            session.close()

catalog_api = CatalogAPI()
