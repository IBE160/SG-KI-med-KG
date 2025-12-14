from uuid import UUID
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.suggestion import SuggestionType, SuggestionStatus

class AISuggestionBase(BaseModel):
    type: SuggestionType
    content: Dict[str, Any]
    rationale: str
    source_reference: str

class AISuggestionCreate(AISuggestionBase):
    document_id: UUID

# Define a minimal UserRead schema here to avoid circular import
class UserReadMinimal(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AISuggestionRead(AISuggestionBase):
    id: UUID
    status: SuggestionStatus
    document_id: UUID
    assigned_bpo: Optional[UserReadMinimal] = None

    model_config = ConfigDict(from_attributes=True)

class AnalysisResult(BaseModel):
    suggestions: list[AISuggestionBase]
