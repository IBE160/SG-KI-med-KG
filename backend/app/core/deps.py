from typing import List, Callable
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_async_session
from app.models.user import User
from app.core.security import get_current_user, UserToken


async def get_current_active_user(
    token_data: UserToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> User:
    """
    Fetch the user from the database using the token's sub (user ID).
    This ensures we get the latest role and data from the database.
    """
    # The 'sub' field in Supabase JWT is the user's UUID
    user_id = token_data.sub

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in database",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


def has_role(roles: List[str]) -> Callable:
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges",
            )
        return current_user

    return role_checker
