from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import String, Column
from app.models.guid import GUID
from app.models.arrays import StringList
from sqlalchemy.orm import relationship
from .base import Base
import uuid


class User(SQLAlchemyBaseUserTableUUID, Base):
    items = relationship("Item", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")

    # New fields for Story 2.5 (Multi-Role)
    # role is deprecated, replaced by roles
    roles = Column(StringList, default=["general_user"], nullable=False)
    
    full_name = Column(String(100), nullable=True)
    # tenant_id is required, but we might need to generate one or assign one.
    # For MVP/dev, allowing null might be safer during migration, but spec says NOT NULL.
    # We will default to a random UUID for now if not provided, or leave nullable=True temporarily
    # until tenant creation logic is solid.
    tenant_id = Column(GUID, default=uuid.uuid4, nullable=False)
