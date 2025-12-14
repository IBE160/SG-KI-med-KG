from typing import Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from pydantic import BaseModel

from app.database import get_async_session
from app.models.user import User as UserModel
from app.models.document import Document
from app.models.suggestion import AISuggestion, SuggestionStatus, SuggestionType
from app.models.compliance import Risk, Control, BusinessProcess
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
    current_user: UserModel = Depends(has_role(["admin", "compliance_officer", "bpo"])),
):
    """
    List AI suggestions with optional status filtering.
    Filtered by tenant - only shows suggestions from documents uploaded by users in the same tenant.
    """
    query = (
        select(AISuggestion)
        .join(Document, AISuggestion.document_id == Document.id)
        .join(UserModel, Document.uploaded_by == UserModel.id)
        .filter(UserModel.tenant_id == current_user.tenant_id)
        .options(joinedload(AISuggestion.assigned_bpo))
    )

    if status:
        query = query.filter(AISuggestion.status == status)

    # Order by creation time (implied by ID usually, or explicit if column existed)
    # Fallback to ID desc for now
    query = query.order_by(AISuggestion.id.desc())

    result = await db.execute(query)
    return result.unique().scalars().all()

from app.services.audit_service import AuditService

@router.patch("/{suggestion_id}/status", response_model=AISuggestionRead, tags=["suggestions"])
async def update_suggestion_status(
    suggestion_id: UUID,
    request: UpdateSuggestionStatusRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(has_role(["admin", "compliance_officer", "bpo"])),
):
    """
    Update the status of an AI suggestion.
    Transitions:
    - pending -> awaiting_bpo_approval (Accept)
    - pending -> rejected (Reject)
    """
    result = await db.execute(
        select(AISuggestion)
        .options(joinedload(AISuggestion.assigned_bpo))
        .where(AISuggestion.id == suggestion_id)
    )
    suggestion = result.scalar_one_or_none()
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
    
    # Handle BPO Assignment
    if request.bpo_id:
        suggestion.assigned_bpo_id = request.bpo_id

    # Audit Log
    changes = {"status": {"old": old_status, "new": request.status}}
    if request.bpo_id:
        changes["assigned_bpo_id"] = str(request.bpo_id)

    await AuditService.log_action(
        db,
        actor_id=current_user.id,
        action=f"SUGGESTION_{request.status.name.upper()}",
        entity_type="AISuggestion",
        entity_id=suggestion.id,
        changes=changes
    )

    # Mock Notification Trigger
    if request.status == SuggestionStatus.pending_review:
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


class ApproveSuggestionRequest(BaseModel):
    name: str
    description: Optional[str] = None


@router.post("/{suggestion_id}/approve", response_model=AISuggestionRead, tags=["suggestions"])
async def approve_suggestion(
    suggestion_id: UUID,
    request: ApproveSuggestionRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(has_role(["admin", "bpo"])),
):
    """
    Approve a suggestion and create the corresponding entity (Risk, Control, or BusinessProcess).
    Only suggestions in pending_review status can be approved.
    """
    # Fetch suggestion with eager loading
    result = await db.execute(
        select(AISuggestion)
        .options(joinedload(AISuggestion.assigned_bpo))
        .where(AISuggestion.id == suggestion_id)
    )
    suggestion = result.scalar_one_or_none()
    if not suggestion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found")

    # Validate status
    if suggestion.status != SuggestionStatus.pending_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only approve suggestions with pending_review status. Current status: {suggestion.status}"
        )

    # Create the appropriate entity based on suggestion type
    entity_id = None
    try:
        if suggestion.type == SuggestionType.risk:
            new_entity = Risk(
                name=request.name,
                description=request.description or "",
                tenant_id=current_user.tenant_id,
            )
            db.add(new_entity)
            await db.flush()
            entity_id = new_entity.id

        elif suggestion.type == SuggestionType.control:
            new_entity = Control(
                name=request.name,
                description=request.description or "",
                tenant_id=current_user.tenant_id,
            )
            db.add(new_entity)
            await db.flush()
            entity_id = new_entity.id

        elif suggestion.type == SuggestionType.business_process:
            new_entity = BusinessProcess(
                name=request.name,
                description=request.description or "",
                tenant_id=current_user.tenant_id,
            )
            db.add(new_entity)
            await db.flush()
            entity_id = new_entity.id

        # Update suggestion status to active
        old_status = suggestion.status
        suggestion.status = SuggestionStatus.active

        # Audit log
        await AuditService.log_action(
            db,
            actor_id=current_user.id,
            action=f"SUGGESTION_APPROVED",
            entity_type=f"{suggestion.type.value.capitalize()}",
            entity_id=entity_id,
            changes={
                "suggestion_id": str(suggestion.id),
                "status": {"old": old_status, "new": "active"},
                "created_entity": {"type": suggestion.type.value, "id": str(entity_id)}
            }
        )

        await db.commit()
        await db.refresh(suggestion)

        print(f"✅ Suggestion {suggestion.id} approved. Created {suggestion.type.value} entity {entity_id}")
        return suggestion

    except Exception as e:
        await db.rollback()
        print(f"❌ Failed to approve suggestion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create entity: {str(e)}"
        )