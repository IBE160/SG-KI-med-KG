from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from app.models.guid import GUID
from datetime import datetime
import uuid

from app.models.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    action = Column(String, nullable=False) # CREATE, UPDATE, DELETE, APPROVE_SUGGESTION
    entity_type = Column(String, nullable=False) # Risk, Control, Suggestion
    entity_id = Column(GUID, nullable=False)
    actor_id = Column(GUID, ForeignKey("user.id"), nullable=False)
    changes = Column(JSON, nullable=True) # JSON diff for updates
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)