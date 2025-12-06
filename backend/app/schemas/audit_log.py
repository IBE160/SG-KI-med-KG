from uuid import UUID
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class AuditLogBase(BaseModel):
    action: str
    entity_type: str
    entity_id: UUID
    changes: Optional[Dict[str, Any]] = None

class AuditLogRead(AuditLogBase):
    id: UUID
    actor_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
