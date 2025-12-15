"""Dashboard API endpoints for role-specific metrics."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from app.database import get_async_session
from app.models.user import User
from app.models.compliance import BusinessProcess
from app.core.deps import get_current_active_user
from app.schemas.dashboard import (
    DashboardMetrics,
    OverviewResponse,
    OverviewProcess,
    OverviewControl,
    OverviewRisk
)
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
        # Use first role as primary role for dashboard display
        role = current_user.roles[0] if current_user.roles else "general_user"

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


@router.get("/overview", response_model=OverviewResponse, tags=["dashboard"])
async def get_overview_data(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
) -> OverviewResponse:
    """
    Retrieve hierarchical overview data (Processes -> Risks/Controls).

    Returns:
        OverviewResponse: List of processes with nested risks and controls.
    """
    try:
        tenant_id = current_user.tenant_id
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no tenant assigned"
            )

        # Fetch processes with related risks and controls eagerly loaded
        query = (
            select(BusinessProcess)
            .options(
                selectinload(BusinessProcess.risks),
                selectinload(BusinessProcess.controls)
            )
            .where(BusinessProcess.tenant_id == tenant_id)
        )
        
        result = await db.execute(query)
        processes = result.scalars().all()

        overview_processes = []
        for proc in processes:
            # Map ORM objects to Pydantic schemas
            controls = [
                OverviewControl(
                    id=c.id,
                    name=c.name,
                    description=c.description,
                    type=c.type
                ) for c in proc.controls
            ]
            
            risks = [
                OverviewRisk(
                    id=r.id,
                    name=r.name,
                    description=r.description,
                    category=r.category
                ) for r in proc.risks
            ]
            
            overview_processes.append(
                OverviewProcess(
                    id=proc.id,
                    name=proc.name,
                    description=proc.description,
                    controls=controls,
                    risks=risks
                )
            )

        return OverviewResponse(processes=overview_processes)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve overview data: {str(e)}"
        )
