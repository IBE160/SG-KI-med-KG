from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from pydantic import BaseModel

from app.database import get_async_session
from app.models.user import User as UserModel
from app.schemas import UserRead, UserUpdate, UserCreate
from app.core.deps import has_role, get_current_active_user
from app.services.user_service import user_service

router = APIRouter()


class RolesUpdate(BaseModel):
    """Schema for updating user roles."""
    roles: list[str]


def validate_role_combination(roles: list[str]) -> tuple[bool, str | None]:
    """
    Validate role combination according to business rules.

    Rules:
    - general_user cannot be combined with other roles
    - All roles must be from allowed set

    Returns:
        (is_valid, error_message)
    """
    if not roles:
        return False, "At least one role is required"

    allowed_roles = {"admin", "bpo", "executive", "general_user"}
    invalid_roles = set(roles) - allowed_roles
    if invalid_roles:
        return False, f"Invalid roles: {', '.join(invalid_roles)}. Allowed: {', '.join(allowed_roles)}"

    # Check mutual exclusivity: general_user cannot combine with other roles
    if "general_user" in roles and len(roles) > 1:
        return False, "general_user cannot be combined with other roles (admin, bpo, executive)"

    return True, None


@router.post("", response_model=UserRead, status_code=201, tags=["users"])
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(has_role(["admin"])),
):
    """
    Create a new user.

    Validates role combination before creation.
    Requires admin role.
    The new user is assigned to the admin's tenant.
    """
    # Validate role combination if roles provided
    if user_in.roles:
        is_valid, error_msg = validate_role_combination(user_in.roles)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

    return await user_service.create_user(user_in, current_user, db)


@router.get("/me", response_model=UserRead, tags=["users"])
async def get_current_user(
    current_user: UserModel = Depends(get_current_active_user),
):
    """
    Get the current authenticated user's information including their role.
    """
    return current_user


@router.get("", response_model=list[UserRead], tags=["users"])
async def list_users(
    role: str | None = None,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(has_role(["admin", "compliance_officer"])),
):
    """
    List users in the current tenant, optionally filtered by role.

    If role parameter is provided, returns users that have that role
    in their roles array.

    Requires admin or compliance_officer role.
    """
    query = select(UserModel).filter(UserModel.tenant_id == current_user.tenant_id)

    if role:
        # Filter users whose roles array contains the specified role
        # For PostgreSQL: WHERE role = ANY(roles)
        from sqlalchemy import any_
        query = query.filter(UserModel.roles.contains([role]))

    result = await db.execute(query)
    return result.scalars().all()


@router.put("/{user_id}/roles", response_model=UserRead, tags=["users"])
async def update_user_roles(
    user_id: UUID,
    roles_update: RolesUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(has_role(["admin"])),
):
    """
    Update user roles with validation.

    Validates that:
    - Roles are from allowed set (admin, bpo, executive, general_user)
    - general_user cannot be combined with other roles

    Requires admin role. Can only update users in the same tenant.
    """
    # Validate role combination
    is_valid, error_msg = validate_role_combination(roles_update.roles)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Ensure admin can only update users in their own tenant
    tenant_id = current_user.tenant_id

    result = await db.execute(select(UserModel).filter(UserModel.id == user_id))
    user_to_update = result.scalars().first()

    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found")

    # Tenant isolation check
    if str(user_to_update.tenant_id) != str(tenant_id):
        raise HTTPException(status_code=404, detail="User not found in your tenant")

    # Update roles
    user_to_update.roles = roles_update.roles

    await db.commit()
    await db.refresh(user_to_update)
    return user_to_update


@router.put("/{user_id}/role", response_model=UserRead, tags=["users"], deprecated=True)
async def update_user_role(
    user_id: UUID,
    role_update: UserUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(has_role(["admin"])),
):
    """
    DEPRECATED: Use PUT /{user_id}/roles instead.

    Legacy endpoint for backward compatibility.
    Updates user with single role as array.
    """
    # Ensure admin can only update users in their own tenant
    tenant_id = current_user.tenant_id

    result = await db.execute(select(UserModel).filter(UserModel.id == user_id))
    user_to_update = result.scalars().first()

    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found")

    # Tenant isolation check
    if str(user_to_update.tenant_id) != str(tenant_id):
        raise HTTPException(status_code=404, detail="User not found in your tenant")

    if role_update.roles:
        # Validate role combination
        is_valid, error_msg = validate_role_combination(role_update.roles)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        user_to_update.roles = role_update.roles

    await db.commit()
    await db.refresh(user_to_update)
    return user_to_update
