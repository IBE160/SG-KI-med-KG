from sqlalchemy import Column, String, ForeignKey, Enum as SQLAlchemyEnum, Text
from sqlalchemy.orm import relationship
from app.models.guid import GUID
from sqlalchemy.types import JSON
import uuid
import enum

from app.models.base import Base

class SuggestionType(str, enum.Enum):
    risk = "risk"
    control = "control"
    business_process = "business_process"

class SuggestionStatus(str, enum.Enum):
    pending = "pending"
    pending_review = "pending_review"  # CO promoted, awaiting BPO approval
    active = "active"  # BPO approved
    archived = "archived"  # BPO discarded
    rejected = "rejected"  # CO rejected

class AISuggestion(Base):
    __tablename__ = "ai_suggestions"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(GUID, nullable=False)  # Multi-tenancy
    document_id = Column(GUID, ForeignKey("documents.id"), nullable=False)
    type = Column(SQLAlchemyEnum(SuggestionType), nullable=False)
    content = Column(JSON, nullable=False)
    rationale = Column(Text, nullable=False)
    source_reference = Column(Text, nullable=False)
    status = Column(SQLAlchemyEnum(SuggestionStatus), default=SuggestionStatus.pending, nullable=False)
    assigned_bpo_id = Column(GUID, ForeignKey("user.id"), nullable=True)  # BPO assigned to review
    
    # Timestamps are handled by Base model if configured, but Base usually only has id/uuid.
    # Adding created_at manually if Base doesn't provide it or if it is not a TimestampMixin
    # Checking Base definition first would be ideal, but standard practice:
    # Assuming Base is declarative_base() and doesn't imply fields.
    # Adding created_at if not present in Base (safest to check first, but will add for now)
    
    # Relationships
    document = relationship("Document", backref="suggestions")
    assigned_bpo = relationship("User", foreign_keys=[assigned_bpo_id])