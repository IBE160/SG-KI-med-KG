import uuid

from fastapi_users import schemas
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from app.models.document import DocumentStatus


class UserRead(schemas.BaseUser[uuid.UUID]):
    role: str
    tenant_id: UUID


class UserCreate(schemas.BaseUserCreate):
    role: str = "general_user"
    tenant_id: UUID | None = None


class UserUpdate(schemas.BaseUserUpdate):
    role: str | None = None
    tenant_id: UUID | None = None


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


# --- Documents ---
class DocumentBase(BaseModel):
    """Base document schema."""
    filename: str = Field(..., max_length=255)


class DocumentCreate(DocumentBase):
    """Schema for creating a document (internal use)."""
    storage_path: str = Field(..., max_length=512)
    uploaded_by: UUID
    status: DocumentStatus = DocumentStatus.pending


class DocumentRead(DocumentBase):
    """Schema for reading a document."""
    id: UUID
    storage_path: str
    status: DocumentStatus
    uploaded_by: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    """Response after successful upload."""
    id: UUID
    filename: str
    status: DocumentStatus
    message: str = "File uploaded successfully and is being processed"

    model_config = {"from_attributes": True}
