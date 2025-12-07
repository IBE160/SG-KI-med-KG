"""Assessment schemas for BPO review and approval of AI suggestions."""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


class ResidualRisk(str, Enum):
    """Residual risk categorization levels for approved controls."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AssessmentAction(str, Enum):
    """Actions available to BPO when assessing AI suggestions."""
    APPROVE = "approve"
    DISCARD = "discard"


class AssessmentRequest(BaseModel):
    """Request payload for BPO assessment action.

    When approving, residual_risk is mandatory. When editing before approval,
    edited field values override the original AI-suggested values.
    """
    action: AssessmentAction = Field(..., description="Assessment action: approve or discard")
    residual_risk: Optional[ResidualRisk] = Field(
        None,
        description="Required for 'approve' action. Categorizes residual risk level."
    )
    edited_risk_description: Optional[str] = Field(
        None,
        description="Edited risk description (overrides AI suggestion if provided)"
    )
    edited_control_description: Optional[str] = Field(
        None,
        description="Edited control description (overrides AI suggestion if provided)"
    )
    edited_business_process: Optional[str] = Field(
        None,
        description="Edited business process name (overrides AI suggestion if provided)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "action": "approve",
                "residual_risk": "medium",
                "edited_risk_description": None,
                "edited_control_description": None,
                "edited_business_process": None
            }
        }


class AssessmentResponse(BaseModel):
    """Response after BPO assessment action.

    Returns success status, updated suggestion status, and audit log reference
    for traceability.
    """
    success: bool = Field(..., description="Whether the assessment action succeeded")
    message: str = Field(..., description="Human-readable success or error message")
    updated_status: str = Field(
        ...,
        description="Updated suggestion status: 'active' (approved) or 'archived' (discarded)"
    )
    audit_log_id: UUID = Field(..., description="Reference to audit log entry for this action")
    active_record_ids: Optional[Dict[str, UUID]] = Field(
        None,
        description="IDs of created active records (business_process_id, risk_id, control_id) if approved"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Successfully added to register",
                "updated_status": "active",
                "audit_log_id": "123e4567-e89b-12d3-a456-426614174000",
                "active_record_ids": {
                    "business_process_id": "550e8400-e29b-41d4-a716-446655440000",
                    "risk_id": "550e8400-e29b-41d4-a716-446655440001",
                    "control_id": "550e8400-e29b-41d4-a716-446655440002"
                }
            }
        }


class PendingReviewItem(BaseModel):
    """Single pending review item for BPO pending reviews list.

    Displays key information about an AI suggestion awaiting BPO approval.
    """
    suggestion_id: UUID = Field(..., description="Unique identifier for the suggestion")
    business_process_name: str = Field(..., description="AI-suggested business process name")
    risk_name: str = Field(..., description="AI-suggested risk name")
    control_name: str = Field(..., description="AI-suggested control name")
    source_reference: str = Field(..., description="Link to original document clause")
    created_at: str = Field(..., description="ISO 8601 timestamp when suggestion was created")

    class Config:
        json_schema_extra = {
            "example": {
                "suggestion_id": "550e8400-e29b-41d4-a716-446655440000",
                "business_process_name": "Customer Data Processing",
                "risk_name": "Unauthorized Access to PII",
                "control_name": "Multi-Factor Authentication",
                "source_reference": "https://example.com/document#clause-3.1.2",
                "created_at": "2025-12-07T10:30:00Z"
            }
        }


class SuggestionDetailResponse(BaseModel):
    """Detailed view of an AI suggestion for BPO assessment.

    Includes full descriptions and rationale needed for decision making.
    """
    suggestion_id: UUID = Field(..., description="Unique identifier for the suggestion")
    business_process_name: str = Field(..., description="AI-suggested business process name")
    risk_name: str = Field(..., description="AI-suggested risk name")
    risk_description: str = Field(..., description="AI-suggested risk description")
    control_name: str = Field(..., description="AI-suggested control name")
    control_description: str = Field(..., description="AI-suggested control description")
    rationale: str = Field(..., description="AI's reasoning for this suggestion")
    source_reference: str = Field(..., description="Link to original document clause")
    created_at: str = Field(..., description="ISO 8601 timestamp when suggestion was created")

    class Config:
        json_schema_extra = {
            "example": {
                "suggestion_id": "550e8400-e29b-41d4-a716-446655440000",
                "business_process_name": "Customer Data Processing",
                "risk_name": "Unauthorized Access to PII",
                "risk_description": "Risk of unauthorized access to PII due to weak auth.",
                "control_name": "Multi-Factor Authentication",
                "control_description": "Implement MFA for all user accounts.",
                "rationale": "MFA is a standard control for protecting PII.",
                "source_reference": "https://example.com/document#clause-3.1.2",
                "created_at": "2025-12-07T10:30:00Z"
            }
        }


class PendingReviewsResponse(BaseModel):
    """Paginated response for BPO pending reviews list."""
    items: list[PendingReviewItem] = Field(..., description="List of pending review items for current page")
    total: int = Field(..., description="Total number of pending reviews for this BPO")
    page: int = Field(..., description="Current page number (1-indexed)")
    size: int = Field(..., description="Page size")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "suggestion_id": 456,
                        "business_process_name": "Customer Data Processing",
                        "risk_name": "Unauthorized Access to PII",
                        "control_name": "Multi-Factor Authentication",
                        "source_reference": "https://example.com/document#clause-3.1.2",
                        "created_at": "2025-12-07T10:30:00Z"
                    }
                ],
                "total": 5,
                "page": 1,
                "size": 20
            }
        }
