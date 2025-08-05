from sqlalchemy import Column,JSON, String, Integer, Numeric, Boolean, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime

from app.databaseConfigs.database import Base

# Association table for many-to-many Product ↔ Categories
product_categories = Table(
    "product_categories",
    Base.metadata,
    Column("product_id", String, ForeignKey("products.id"), primary_key=True),
    Column("category_id", String, ForeignKey("categories.id"), primary_key=True)
)

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    sku = Column(Integer, nullable=False)  # Stock Keeping Unit
    name = Column(String, nullable=False)
    thumbnail = Column(String, nullable=False)
    images = Column(JSON, nullable=True)
    description = Column(String)

    price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2), nullable=False)
    discount = Column(Integer, default=0)
    max_discount = Column(Integer)

    gender = Column(String)  # e.g., Male, Female, Unisex
    age_group = Column(String)  # e.g., Kids, Adults

    max_order_count = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    categories = relationship("Category", secondary=product_categories, back_populates="products")
    sizes = relationship("ProductSize", back_populates="product", cascade="all, delete-orphan")
