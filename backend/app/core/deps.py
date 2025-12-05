from typing import List, Callable
from fastapi import Depends, HTTPException, status
from app.database import User
from app.core.security import get_current_user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    # In this setup, Supabase handles active state, but we can double check DB if needed
    # For now, assuming if they have a valid token, they are active
    return current_user

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

def has_role(roles: List[str]) -> Callable:
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges"
            )
        return current_user
    return role_checker
