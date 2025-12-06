from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from app.database import get_async_session
from app.models.user import User as UserModel
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogRead
from app.core.deps import has_role

router = APIRouter()

@router.get("", response_model=List[AuditLogRead], tags=["audit-logs"])
async def list_audit_logs(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[UUID] = Query(None, description="Filter by entity ID"),
    actor_id: Optional[UUID] = Query(None, description="Filter by actor ID"),
    db: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(has_role(["admin", "compliance_officer"])),
):
    """
    Retrieve audit logs.
    Requires admin or compliance_officer role.
    """
    query = select(AuditLog)

    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if actor_id:
        query = query.filter(AuditLog.actor_id == actor_id)
        
    # Order by most recent
    query = query.order_by(AuditLog.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()
