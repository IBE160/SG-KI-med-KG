from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from app.models.suggestion import SuggestionStatus, SuggestionType
from app.schemas import UserRead


class AISuggestionBase(BaseModel):
    document_id: UUID
    type: SuggestionType
    content: dict[str, Any]
    rationale: str
    source_reference: str
    status: SuggestionStatus
    tenant_id: UUID


class AISuggestionCreate(AISuggestionBase):
    pass


class AISuggestionUpdate(BaseModel):
    status: Optional[SuggestionStatus] = None
    content: Optional[dict[str, Any]] = None
    assigned_bpo_id: Optional[UUID] = None


class AISuggestionRead(AISuggestionBase):
    id: UUID
    assigned_bpo_id: Optional[UUID] = None
    assigned_bpo: Optional[UserRead] = None

    model_config = ConfigDict(from_attributes=True)
