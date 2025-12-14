from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.user import User
from app.core.deps import get_current_active_user
from app.schemas.reports import GapAnalysisReport
from app.services.gap_analysis_service import GapAnalysisService

router = APIRouter()


def verify_admin_or_executive_role(current_user: User) -> None:
    """Verify that the current user has Admin or Executive role."""
    if not any(role in current_user.roles for role in ["admin", "executive"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This endpoint requires Admin or Executive role.",
        )


@router.get(
    "/gap-analysis/{framework_id}",
    response_model=GapAnalysisReport,
    status_code=status.HTTP_200_OK,
    tags=["reports"],
)
async def generate_gap_analysis_report(
    framework_id: UUID = Path(..., description="UUID of the regulatory framework"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
) -> GapAnalysisReport:
    """
    Generate a gap analysis report for a selected regulatory framework.
    
    Identifies regulatory requirements with no associated controls.
    Accessible to Admin and Executive roles.
    
    Args:
        framework_id: UUID of the regulatory framework
        db: Database session
        current_user: Authenticated user from JWT
        
    Returns:
        GapAnalysisReport: Structured report
        
    Raises:
        401: Unauthorized
        403: Forbidden (non-Admin/Executive)
        404: Not Found (framework doesn't exist)
    """
    verify_admin_or_executive_role(current_user)
    
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no tenant assigned",
        )
        
    return await GapAnalysisService.generate_report(
        db=db,
        framework_id=framework_id,
        tenant_id=current_user.tenant_id
    )
