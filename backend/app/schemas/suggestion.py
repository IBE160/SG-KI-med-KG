from uuid import UUID
from typing import Dict, Any
from pydantic import BaseModel, Field
from app.models.suggestion import SuggestionType, SuggestionStatus

class AISuggestionBase(BaseModel):
    type: SuggestionType
    content: Dict[str, Any]
    rationale: str
    source_reference: str

class AISuggestionCreate(AISuggestionBase):
    document_id: UUID

class AISuggestionRead(AISuggestionBase):
    id: UUID
    status: SuggestionStatus
    document_id: UUID

    class Config:
        from_attributes = True

class AnalysisResult(BaseModel):
    suggestions: list[AISuggestionBase]
