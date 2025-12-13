from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from app.models.guid import GUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from .base import Base


class DocumentStatus(str, enum.Enum):
    """Status of document processing."""
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    storage_path = Column(String(512), nullable=False)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.pending, nullable=False)
    # Using GUID for uploaded_by for better type safety and consistency
    uploaded_by = Column(GUID, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    archived_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="documents")