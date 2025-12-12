"""Compliance Mapping API endpoints for Admin users."""

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_async_session
from app.models.user import User
from app.core.deps import get_current_active_user
from app.schemas.mapping import (
    MappingCreate,
    MappingDelete,
    MappingDetail,
    MappingListResponse,
)
from app.services.mapping_service import MappingService

router = APIRouter()


def verify_admin_role(current_user: User) -> None:
    """Verify that the current user has Admin role.

    Args:
        current_user: Authenticated user from JWT

    Raises:
        HTTPException: 403 Forbidden if user is not Admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This endpoint requires Admin role.",
        )


def verify_read_access(current_user: User) -> None:
    """Verify that the current user has read access (Admin, Executive, or BPO).

    Args:
        current_user: Authenticated user from JWT

    Raises:
        HTTPException: 403 Forbidden if user doesn't have read access
    """
    if current_user.role not in ["admin", "executive", "bpo"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This endpoint requires Admin, Executive, or BPO role.",
        )


@router.post("", response_model=MappingDetail, status_code=status.HTTP_201_CREATED, tags=["mappings"])
async def create_mapping(
    payload: MappingCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
) -> MappingDetail:
    """
    Create a new control-to-requirement mapping.

    Only accessible to Admin users. Validates that both control and requirement
    exist in the user's tenant, prevents duplicate mappings, and logs the action
    to the audit trail.

    Args:
        payload: MappingCreate with control_id and regulatory_requirement_id
        db: Database session
        current_user: Authenticated user from JWT

    Returns:
        MappingDetail: Created mapping with control and requirement names

    Raises:
        401: Unauthorized (JWT missing/invalid)
        403: Forbidden (non-Admin user)
        400: Bad Request (invalid control_id or requirement_id)
        409: Conflict (mapping already exists)
    """
    # Verify Admin role
    verify_admin_role(current_user)

    # Validate tenant_id exists
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no tenant assigned",
        )

    mapping = await MappingService.create_mapping(
        db=db,
        control_id=payload.control_id,
        requirement_id=payload.regulatory_requirement_id,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
    )

    await db.commit()
    return mapping


@router.delete("", status_code=status.HTTP_204_NO_CONTENT, tags=["mappings"])
async def delete_mapping(
    payload: MappingDelete,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a control-to-requirement mapping.

    Only accessible to Admin users. Idempotent operation - returns 404 if
    mapping doesn't exist. Logs the deletion to the audit trail.

    Args:
        payload: MappingDelete with control_id and regulatory_requirement_id
        db: Database session
        current_user: Authenticated user from JWT

    Raises:
        401: Unauthorized (JWT missing/invalid)
        403: Forbidden (non-Admin user)
        404: Not Found (mapping doesn't exist)
    """
    # Verify Admin role
    verify_admin_role(current_user)

    # Validate tenant_id exists
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no tenant assigned",
        )

    await MappingService.delete_mapping(
        db=db,
        control_id=payload.control_id,
        requirement_id=payload.regulatory_requirement_id,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
    )

    await db.commit()


@router.get(
    "/control/{control_id}",
    response_model=MappingListResponse,
    tags=["mappings"],
)
async def get_mappings_for_control(
    control_id: UUID = Path(..., description="UUID of the control"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
) -> MappingListResponse:
    """
    Get all regulatory requirements mapped to a specific control.

    Accessible to Admin, Executive, and BPO users. Returns list of mappings
    with requirement names for display.

    Args:
        control_id: UUID of the control
        db: Database session
        current_user: Authenticated user from JWT

    Returns:
        MappingListResponse: List of mappings with total count

    Raises:
        401: Unauthorized (JWT missing/invalid)
        403: Forbidden (non-Admin/Executive/BPO user)
        404: Not Found (control doesn't exist or not in user's tenant)
    """
    # Verify read access
    verify_read_access(current_user)

    # Validate tenant_id exists
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no tenant assigned",
        )

    return await MappingService.get_mappings_for_control(
        db=db, control_id=control_id, tenant_id=current_user.tenant_id
    )


@router.get(
    "/requirement/{requirement_id}",
    response_model=MappingListResponse,
    tags=["mappings"],
)
async def get_mappings_for_requirement(
    requirement_id: UUID = Path(..., description="UUID of the regulatory requirement"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
) -> MappingListResponse:
    """
    Get all controls mapped to a specific regulatory requirement.

    Accessible to Admin, Executive, and BPO users. Returns list of mappings
    with control names for display.

    Args:
        requirement_id: UUID of the regulatory requirement
        db: Database session
        current_user: Authenticated user from JWT

    Returns:
        MappingListResponse: List of mappings with total count

    Raises:
        401: Unauthorized (JWT missing/invalid)
        403: Forbidden (non-Admin/Executive/BPO user)
        404: Not Found (requirement doesn't exist or not in user's tenant)
    """
    # Verify read access
    verify_read_access(current_user)

    # Validate tenant_id exists
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no tenant assigned",
        )

    return await MappingService.get_mappings_for_requirement(
        db=db, requirement_id=requirement_id, tenant_id=current_user.tenant_id
    )
