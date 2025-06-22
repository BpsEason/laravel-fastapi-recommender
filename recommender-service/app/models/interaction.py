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
    # Laravel Models will automatically manage created_at/updated_at.
    # If a separate 'timestamp' column is required and should reflect creation time,
    # it's usually managed by the database (e.g., default CURRENT_TIMESTAMP)
    # or set manually in Laravel before saving.
    # FastAPI's SQLAlchemy model here maps to existing Laravel table schema.
    timestamp = Column(DateTime, default=func.now()) # This will be automatically set by SQLAlchemy on insert
    # created_at and updated_at might also exist in the table if Laravel added them
    # but for FastAPI's read-only purpose, 'timestamp' might be the relevant one for interaction time.
