from uuid import UUID
from typing import List
from pydantic import BaseModel
from datetime import datetime


class MappingCreate(BaseModel):
    """Request to create a new control-requirement mapping"""

    control_id: UUID
    regulatory_requirement_id: UUID


class MappingDelete(BaseModel):
    """Request to delete a mapping"""

    control_id: UUID
    regulatory_requirement_id: UUID


class MappingDetail(BaseModel):
    """Single mapping record"""

    id: UUID
    control_id: UUID
    regulatory_requirement_id: UUID
    control_name: str
    requirement_name: str
    created_at: datetime
    created_by: UUID

    class Config:
        from_attributes = True


class MappingListResponse(BaseModel):
    """List of mappings for a control or requirement"""

    total: int
    mappings: List[MappingDetail]
