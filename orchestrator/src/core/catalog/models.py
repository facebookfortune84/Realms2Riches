from sqlalchemy import Column, String, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship, declarative_base
from pydantic import BaseModel
from typing import Optional, List

# --- SQLAlchemy Models ---
from orchestrator.src.memory.sql_store import Base

class ProductModel(Base):
    __tablename__ = 'products'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    category = Column(String)
    
    prices = relationship("PriceModel", back_populates="product", cascade="all, delete-orphan")

class PriceModel(Base):
    __tablename__ = 'prices'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String, ForeignKey('products.id'), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    interval = Column(String) # 'month', 'year', 'one_time'
    stripe_price_id = Column(String)
    
    product = relationship("ProductModel", back_populates="prices")

# --- Pydantic Schemas ---

class PriceSchema(BaseModel):
    product_id: str
    price: float
    currency: str
    interval: str
    stripe_price_id: Optional[str] = None

class ProductSchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    category: str
    prices: List[PriceSchema] = []
