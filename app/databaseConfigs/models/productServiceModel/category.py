from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.databaseConfigs.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False, unique=True)
    description = Column(String)

    products = relationship("Product", secondary="product_categories", back_populates="categories")
