"""Assessment API endpoints for BPO review and approval of AI suggestions."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.database import get_async_session
from app.models.user import User
from app.models.suggestion import AISuggestion
from app.core.deps import get_current_active_user
from app.schemas.assessment import (
    AssessmentRequest,
    AssessmentResponse,
    PendingReviewsResponse,
    PendingReviewItem,
    SuggestionDetailResponse
)
from app.services.assessment_service import AssessmentService
from uuid import UUID


router = APIRouter()


def verify_bpo_role(current_user: User) -> None:
    """Verify that the current user has BPO role.

    Args:
        current_user: Authenticated user from JWT

    Raises:
        HTTPException: 403 Forbidden if user is not BPO
    """
    if current_user.role != "bpo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This endpoint requires BPO role."
        )


@router.get("/pending", response_model=PendingReviewsResponse, tags=["assessments"])
async def get_pending_reviews(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(20, ge=1, le=100, description="Page size (max 100)"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
) -> PendingReviewsResponse:
    """
    Retrieve paginated list of suggestions with status 'pending_review' assigned to the logged-in BPO.

    Only accessible to users with BPO role. Returns suggestions filtered by:
    - status = "pending_review"
    - assigned_bpo_id = current_user.id
    - tenant_id = current_user.tenant_id (enforced by RLS)

    Args:
        page: Page number (1-indexed)
        size: Number of items per page (max 100)
        db: Database session
        current_user: Authenticated user from JWT

    Returns:
        PendingReviewsResponse: Paginated list of pending review items

    Raises:
        401: Unauthorized (JWT missing/invalid)
        403: Forbidden (non-BPO user or user has no tenant)
        500: Internal server error
    """
    # Verify BPO role
    verify_bpo_role(current_user)

    # Validate tenant_id exists
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no tenant assigned"
        )

    try:
        # Calculate offset for pagination
        offset = (page - 1) * size

        # Query suggestions with status "pending_review" assigned to this BPO
        query = select(AISuggestion).where(
            AISuggestion.status == "pending_review",
            AISuggestion.assigned_bpo_id == current_user.id,
            AISuggestion.tenant_id == current_user.tenant_id
        ).offset(offset).limit(size)

        result = await db.execute(query)
        suggestions = result.scalars().all()

        # Count total pending reviews for this BPO
        count_query = select(AISuggestion).where(
            AISuggestion.status == "pending_review",
            AISuggestion.assigned_bpo_id == current_user.id,
            AISuggestion.tenant_id == current_user.tenant_id
        )
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # Transform suggestions to PendingReviewItem schema
        items = []
        for suggestion in suggestions:
            content = suggestion.content if isinstance(suggestion.content, dict) else {}
            items.append(
                PendingReviewItem(
                    suggestion_id=suggestion.id,
                    business_process_name=content.get("business_process_name", "Unnamed Process"),
                    risk_name=content.get("risk_name", "Unnamed Risk"),
                    control_name=content.get("control_name", "Unnamed Control"),
                    source_reference=suggestion.source_reference,
                    created_at=suggestion.created_at.isoformat() if hasattr(suggestion, 'created_at') else ""
                )
            )

        return PendingReviewsResponse(
            items=items,
            total=total,
            page=page,
            size=size
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve pending reviews: {str(e)}"
        )


@router.get("/{suggestion_id}", response_model=SuggestionDetailResponse, tags=["assessments"])
async def get_suggestion_detail(
    suggestion_id: UUID = Path(..., description="ID of the suggestion to retrieve"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
) -> SuggestionDetailResponse:
    """
    Retrieve detailed information for a specific AI suggestion.

    Only accessible to BPO assigned to the suggestion.

    Args:
        suggestion_id: ID of the suggestion
        db: Database session
        current_user: Authenticated user from JWT

    Returns:
        SuggestionDetailResponse: Detailed suggestion data

    Raises:
        403: Forbidden (not BPO or not assigned)
        404: Not Found
    """
    verify_bpo_role(current_user)

    if not current_user.tenant_id:
        raise HTTPException(status_code=403, detail="User has no tenant assigned")

    result = await db.execute(
        select(AISuggestion).where(
            AISuggestion.id == suggestion_id,
            AISuggestion.tenant_id == current_user.tenant_id
        )
    )
    suggestion = result.scalar_one_or_none()

    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    if suggestion.assigned_bpo_id != current_user.id:
        raise HTTPException(status_code=403, detail="Suggestion not assigned to you")

    content = suggestion.content if isinstance(suggestion.content, dict) else {}
    
    return SuggestionDetailResponse(
        suggestion_id=suggestion.id,
        business_process_name=content.get("business_process_name", "Unnamed Process"),
        risk_name=content.get("risk_name", "Unnamed Risk"),
        risk_description=content.get("risk_description", ""),
        control_name=content.get("control_name", "Unnamed Control"),
        control_description=content.get("control_description", ""),
        rationale=suggestion.rationale,
        source_reference=suggestion.source_reference,
        created_at=suggestion.created_at.isoformat() if hasattr(suggestion, 'created_at') else ""
    )


@router.post("/{suggestion_id}/assess", response_model=AssessmentResponse, tags=["assessments"])
async def submit_assessment(
    suggestion_id: UUID = Path(..., description="ID of the suggestion to assess"),
    request: AssessmentRequest = ...,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
) -> AssessmentResponse:
    """
    Submit BPO assessment action (approve or discard) for an AI suggestion.

    Authorization checks:
    - User must have BPO role
    - Suggestion.assigned_bpo_id must match current_user.id
    - Suggestion.tenant_id must match current_user.tenant_id (enforced by service layer)

    Validation:
    - For approve action: residual_risk is REQUIRED (400 Bad Request if missing)
    - Suggestion must exist and have status "pending_review" (404 if not found, 409 if wrong status)

    Side effects:
    - Approve: Creates active records (business_process, risk, control), updates status to "active"
    - Discard: Updates status to "archived"
    - Both actions: Creates immutable audit log entry

    Args:
        suggestion_id: ID of the suggestion to assess
        request: AssessmentRequest with action, residual_risk (if approve), and optional edits
        db: Database session
        current_user: Authenticated user from JWT

    Returns:
        AssessmentResponse: Success status, message, updated status, audit_log_id, and active_record_ids (if approved)

    Raises:
        400: Bad Request (residual_risk missing for approve action)
        401: Unauthorized (JWT missing/invalid)
        403: Forbidden (non-BPO user, not assigned to this suggestion, or no tenant)
        404: Not Found (suggestion doesn't exist or belongs to different tenant)
        409: Conflict (suggestion status is not "pending_review")
        500: Internal server error
    """
    # Verify BPO role
    verify_bpo_role(current_user)

    # Validate tenant_id exists
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no tenant assigned"
        )

    # Validate residual_risk is present for approve action
    if request.action == "approve" and not request.residual_risk:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Residual risk is required for approve action"
        )

    try:
        # Fetch suggestion to verify assigned_bpo_id matches current user
        result = await db.execute(
            select(AISuggestion).where(
                AISuggestion.id == suggestion_id,
                AISuggestion.tenant_id == current_user.tenant_id
            )
        )
        suggestion = result.scalar_one_or_none()

        if not suggestion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Suggestion {suggestion_id} not found or not accessible"
            )

        # Verify assigned_bpo_id matches current user
        if suggestion.assigned_bpo_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Suggestion {suggestion_id} is not assigned to you"
            )

        # Prepare edits dictionary if provided
        edits = None
        if (request.edited_risk_description or
            request.edited_control_description or
            request.edited_business_process):
            edits = {
                "edited_risk_description": request.edited_risk_description,
                "edited_control_description": request.edited_control_description,
                "edited_business_process": request.edited_business_process
            }

        # Call AssessmentService based on action
        if request.action == "approve":
            response = await AssessmentService.approve_suggestion(
                db=db,
                suggestion_id=suggestion_id,
                residual_risk=request.residual_risk,
                edits=edits,
                actor_id=current_user.id,
                tenant_id=current_user.tenant_id
            )
        elif request.action == "discard":
            response = await AssessmentService.discard_suggestion(
                db=db,
                suggestion_id=suggestion_id,
                actor_id=current_user.id,
                tenant_id=current_user.tenant_id
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action: {request.action}. Must be 'approve' or 'discard'."
            )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        # Handle ValueError from AssessmentService (e.g., wrong status, missing residual_risk)
        if "expected 'pending_review'" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit assessment: {str(e)}"
        )
