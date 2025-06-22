from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base

class UserInteraction(Base):
    __tablename__ = "user_interactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    interaction_type = Column(String(255), index=True)
    timestamp = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="interactions")
    product = relationship("Product", back_populates="user_interactions")
