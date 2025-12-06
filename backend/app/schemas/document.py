from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.document import DocumentStatus


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

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """Response after successful upload."""
    id: UUID
    filename: str
    status: DocumentStatus
    message: str = "File uploaded successfully and is being processed"

    class Config:
        from_attributes = True
