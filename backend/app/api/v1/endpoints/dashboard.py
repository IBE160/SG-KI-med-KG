"""Dashboard API endpoints for role-specific metrics."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.user import User
from app.core.deps import get_current_active_user
from app.schemas.dashboard import DashboardMetrics
from app.services.dashboard_service import DashboardService


router = APIRouter()


@router.get("/metrics", response_model=DashboardMetrics, tags=["dashboard"])
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
) -> DashboardMetrics:
    """
    Retrieve role-specific dashboard metrics for the authenticated user.

    Returns:
        DashboardMetrics: Role-specific dashboard cards and data

    Raises:
        401: Unauthorized (JWT missing/invalid)
        403: Forbidden (user inactive or invalid tenant)
        500: Internal server error (database/service failure)
    """
    try:
        # Extract user info from JWT (already validated by get_current_active_user)
        user_id = current_user.id
        tenant_id = current_user.tenant_id
        role = current_user.role

        # Validate tenant_id exists (should be set during user creation)
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no tenant assigned"
            )

        # Call DashboardService to aggregate metrics
        metrics = await DashboardService.get_metrics(
            db=db,
            user_id=user_id,
            tenant_id=tenant_id,
            role=role
        )

        return metrics

    except HTTPException:
        # Re-raise HTTP exceptions (like 403)
        raise
    except Exception as e:
        # Log error and return 500 for unexpected failures
        # TODO: Add structured logging here
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard metrics: {str(e)}"
        )
