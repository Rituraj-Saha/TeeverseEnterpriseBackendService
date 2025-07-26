from sqlalchemy import Column, String, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.databaseConfigs.database import Base

class ProductSize(Base):
    __tablename__ = "product_sizes"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    size = Column(String, nullable=False)  # e.g., S, M, L, XL
    stock = Column(Integer, nullable=False, default=0)
    additional_price = Column(Numeric(10, 2), default=0.00)

    product = relationship("Product", back_populates="sizes")
