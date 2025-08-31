# app/cartService/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.databaseConfigs.database import Base
from uuid import uuid4

class Cart(Base):
    __tablename__ = "carts"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(Integer, ForeignKey("users.userid"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    requested_qty = Column(Integer, nullable=False)
    requested_size = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="cart_items")
    product = relationship("Product", backref="cart_entries")
