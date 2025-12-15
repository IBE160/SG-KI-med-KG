from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class ControlBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: Optional[str] = None
    owner_id: Optional[UUID] = None

class ControlCreate(ControlBase):
    pass

class ControlUpdate(ControlBase):
    pass

class Control(ControlBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Regulatory Schemas ---

class RegulatoryRequirementBase(BaseModel):
    name: str
    description: Optional[str] = None
    document_id: Optional[UUID] = None

class RegulatoryRequirementCreate(RegulatoryRequirementBase):
    framework_id: UUID

class RegulatoryRequirementRead(RegulatoryRequirementBase):
    id: UUID
    framework_id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class RegulatoryFrameworkBase(BaseModel):
    name: str
    description: Optional[str] = None
    version: Optional[str] = None
    document_id: Optional[UUID] = None

class RegulatoryFrameworkCreate(RegulatoryFrameworkBase):
    pass

class RegulatoryFrameworkRead(RegulatoryFrameworkBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class RegulatoryFrameworkTreeItem(RegulatoryFrameworkRead):
    requirements: List[RegulatoryRequirementRead] = []

    model_config = {"from_attributes": True}
