import uuid
from typing import TYPE_CHECKING, Optional

from fastapi_users import schemas
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from app.models.document import DocumentStatus

# Use TYPE_CHECKING to avoid circular import
if TYPE_CHECKING:
    from app.services.ai_service import DocumentClassification


class UserRead(schemas.BaseUser[uuid.UUID]):
    roles: list[str]
    tenant_id: UUID
    full_name: str | None = None


class UserCreate(schemas.BaseUserCreate):
    roles: list[str] = ["general_user"]
    tenant_id: UUID | None = None
    full_name: str | None = None


class UserUpdate(schemas.BaseUserUpdate):
    roles: list[str] | None = None
    tenant_id: UUID | None = None
    full_name: str | None = None


class ItemBase(BaseModel):
    name: str
    description: str | None = None
    quantity: int | None = None


class ItemCreate(ItemBase):
    pass


class ItemRead(ItemBase):
    id: UUID
    user_id: UUID

    model_config = {"from_attributes": True}


# --- Business Processes ---
class BusinessProcessBase(BaseModel):
    name: str
    description: str | None = None


class BusinessProcessCreate(BusinessProcessBase):
    pass


class BusinessProcessUpdate(BusinessProcessBase):
    pass


class BusinessProcessRead(BusinessProcessBase):
    id: UUID
    tenant_id: UUID
    owner_id: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Risks ---
class RiskBase(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None


class RiskCreate(RiskBase):
    pass


class RiskUpdate(RiskBase):
    pass


class RiskRead(RiskBase):
    id: UUID
    tenant_id: UUID
    owner_id: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Controls ---
class ControlBase(BaseModel):
    name: str
    description: str | None = None
    type: str | None = None


class ControlCreate(ControlBase):
    pass


class ControlUpdate(ControlBase):
    pass


class ControlRead(ControlBase):
    id: UUID
    tenant_id: UUID
    owner_id: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Regulatory Frameworks ---
class RegulatoryFrameworkBase(BaseModel):
    name: str
    description: str | None = None
    version: str | None = None


class RegulatoryFrameworkCreate(RegulatoryFrameworkBase):
    pass


class RegulatoryFrameworkUpdate(RegulatoryFrameworkBase):
    pass


class RegulatoryFrameworkRead(RegulatoryFrameworkBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Regulatory Requirements ---
class RegulatoryRequirementBase(BaseModel):
    name: str
    description: str | None = None
    framework_id: UUID


class RegulatoryRequirementCreate(RegulatoryRequirementBase):
    pass


class RegulatoryRequirementUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    framework_id: UUID | None = None


class RegulatoryRequirementRead(RegulatoryRequirementBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Documents ---
# Import DocumentRead and DocumentUploadResponse from document.py to include classification
from app.schemas.document import DocumentBase, DocumentCreate, DocumentRead, DocumentUploadResponse
