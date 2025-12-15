from typing import List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import get_async_session
from app.models.user import User
from app.models.compliance import RegulatoryFramework
from app.schemas.compliance import RegulatoryFrameworkTreeItem
from app.core.deps import has_role

router = APIRouter()

@router.get("/tree", response_model=List[RegulatoryFrameworkTreeItem])
async def get_regulatory_frameworks_tree(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(has_role(["admin", "bpo", "executive", "auditor"])),
) -> Any:
    """
    Get all regulatory frameworks with their requirements in a hierarchical tree structure.
    """
    stmt = (
        select(RegulatoryFramework)
        .filter(RegulatoryFramework.tenant_id == current_user.tenant_id)
        .options(selectinload(RegulatoryFramework.requirements))
        .order_by(RegulatoryFramework.name)
    )
    result = await db.execute(stmt)
    frameworks = result.scalars().all()
    
    return frameworks
