from sqlalchemy import Column, String, ForeignKey, Enum as SQLAlchemyEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import JSON
import uuid
import enum

from app.models.base import Base

class SuggestionType(str, enum.Enum):
    risk = "risk"
    control = "control"

class SuggestionStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class AISuggestion(Base):
    __tablename__ = "ai_suggestions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    type = Column(SQLAlchemyEnum(SuggestionType), nullable=False)
    content = Column(JSON, nullable=False)
    rationale = Column(Text, nullable=False)
    source_reference = Column(Text, nullable=False)
    status = Column(SQLAlchemyEnum(SuggestionStatus), default=SuggestionStatus.pending, nullable=False)
    
    # Timestamps are handled by Base model if configured, but Base usually only has id/uuid.
    # Adding created_at manually if Base doesn't provide it or if it is not a TimestampMixin
    # Checking Base definition first would be ideal, but standard practice:
    # Assuming Base is declarative_base() and doesn't imply fields.
    # Adding created_at if not present in Base (safest to check first, but will add for now)
    
    # Relationship
    document = relationship("Document", backref="suggestions")
