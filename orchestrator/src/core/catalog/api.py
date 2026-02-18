from typing import List, Optional
from orchestrator.src.core.catalog.models import ProductModel, PriceModel, ProductSchema, PriceSchema
from orchestrator.src.memory.sql_store import SQLStore
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class CatalogAPI:
    def __init__(self):
        self.store = SQLStore()
    
    def get_products(self) -> List[ProductSchema]:
        """Fetch all products with their pricing."""
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
                            interval=pr.interval
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
                        interval=pr.interval
                    ) for pr in p.prices
                ]
            )
        finally:
            session.close()

catalog_api = CatalogAPI()
