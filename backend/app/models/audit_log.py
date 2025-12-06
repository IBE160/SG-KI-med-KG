from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.models.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action = Column(String, nullable=False) # CREATE, UPDATE, DELETE, APPROVE_SUGGESTION
    entity_type = Column(String, nullable=False) # Risk, Control, Suggestion
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    changes = Column(JSON, nullable=True) # JSON diff for updates
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
