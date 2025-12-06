from typing import Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from pydantic import BaseModel

from app.database import get_async_session
from app.models.user import User as UserModel
from app.models.suggestion import AISuggestion, SuggestionStatus
from app.schemas.suggestion import AISuggestionRead
from app.core.deps import has_role

router = APIRouter()

class UpdateSuggestionStatusRequest(BaseModel):
    status: SuggestionStatus
    updated_content: Optional[dict[str, Any]] = None
    bpo_id: Optional[UUID] = None

@router.get("", response_model=List[AISuggestionRead], tags=["suggestions"])
async def list_suggestions(
    status: Optional[SuggestionStatus] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(has_role(["admin", "compliance_officer"])),
):
    """
    List AI suggestions with optional status filtering.
    """
    query = select(AISuggestion)
    if status:
        query = query.filter(AISuggestion.status == status)
    
    # Order by creation time (implied by ID usually, or explicit if column existed)
    # Fallback to ID desc for now
    query = query.order_by(AISuggestion.id.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

from app.services.audit_service import AuditService

@router.patch("/{suggestion_id}/status", response_model=AISuggestionRead, tags=["suggestions"])
async def update_suggestion_status(
    suggestion_id: UUID,
    request: UpdateSuggestionStatusRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(has_role(["admin", "compliance_officer"])),
):
    """
    Update the status of an AI suggestion.
    Transitions:
    - pending -> awaiting_bpo_approval (Accept)
    - pending -> rejected (Reject)
    """
    suggestion = await db.get(AISuggestion, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found")

    # Validate State Transitions
    if suggestion.status != SuggestionStatus.pending:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot transition from {suggestion.status} status.")

    # Prepare Audit Changes
    old_status = suggestion.status
    
    # Update fields
    suggestion.status = request.status
    if request.updated_content:
        suggestion.content = request.updated_content
    
    # Audit Log
    await AuditService.log_action(
        db,
        actor_id=current_user.id,
        action=f"SUGGESTION_{request.status.name.upper()}",
        entity_type="AISuggestion",
        entity_id=suggestion.id,
        changes={"status": {"old": old_status, "new": request.status}}
    )

    # Mock Notification Trigger
    if request.status == SuggestionStatus.awaiting_bpo_approval:
        if request.bpo_id:
            # Send notification logic here (mocked)
            print(f"Sending notification to BPO {request.bpo_id} for suggestion {suggestion_id}")
        else:
             # If BPO assignment is mandatory for acceptance, raise error or auto-assign
             # For MVP, we log a warning if no BPO provided but proceed
             print(f"Warning: Suggestion accepted without BPO assignment.")

    await db.commit()
    await db.refresh(suggestion)
    return suggestion