from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from app.database import get_async_session
from app.models.user import User as UserModel
from app.schemas import UserRead, UserUpdate
from app.core.deps import has_role, get_current_active_user

router = APIRouter()


@router.get("/me", response_model=UserRead, tags=["users"])
async def get_current_user(
    current_user: UserModel = Depends(get_current_active_user),
):
    """
    Get the current authenticated user's information including their role.
    """
    return current_user


@router.put("/{user_id}/role", response_model=UserRead, tags=["users"])
async def update_user_role(
    user_id: UUID,
    role_update: UserUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(has_role(["admin"])),
):
    # Ensure admin can only update users in their own tenant
    tenant_id = current_user.tenant_id

    result = await db.execute(select(UserModel).filter(UserModel.id == user_id))
    user_to_update = result.scalars().first()

    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found")

    # Tenant isolation check
    if str(user_to_update.tenant_id) != str(tenant_id):
        raise HTTPException(status_code=404, detail="User not found in your tenant")

    if role_update.role:
        # Validate role against allowed values
        allowed_roles = ["admin", "bpo", "executive", "general_user"]
        if role_update.role not in allowed_roles:
            raise HTTPException(
                status_code=400, detail=f"Invalid role. Allowed: {allowed_roles}"
            )

        user_to_update.role = role_update.role

    await db.commit()
    await db.refresh(user_to_update)
    return user_to_update
