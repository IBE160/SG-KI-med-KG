from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import String, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base
import uuid

class User(SQLAlchemyBaseUserTableUUID, Base):
    items = relationship("Item", back_populates="user", cascade="all, delete-orphan")
    
    # New fields for Story 2.1
    role = Column(String(50), default="general_user", nullable=False)
    # tenant_id is required, but we might need to generate one or assign one. 
    # For MVP/dev, allowing null might be safer during migration, but spec says NOT NULL.
    # We will default to a random UUID for now if not provided, or leave nullable=True temporarily 
    # until tenant creation logic is solid.
    tenant_id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)