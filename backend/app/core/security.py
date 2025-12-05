from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel

from app.config import settings

# Reusable OAuth2 scheme
security = HTTPBearer()

class UserToken(BaseModel):
    sub: str
    email: Optional[str] = None
    role: Optional[str] = "general_user"
    tenant_id: Optional[str] = None
    exp: int
    iat: int
    aud: Optional[str] = None

    class Config:
        extra = "ignore"

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserToken:
    """
    Validates the Supabase JWT and returns the user claims.
    """
    token = credentials.credentials
    
    if not settings.SUPABASE_JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase JWT secret not configured"
        )

    try:
        # Decode and validate the token
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated" # Supabase default audience
        )
        
        # Extract custom claims if they exist (role, tenant_id often in app_metadata or user_metadata)
        # Supabase puts custom claims in app_metadata usually
        app_metadata = payload.get("app_metadata", {})
        user_metadata = payload.get("user_metadata", {})
        
        role = app_metadata.get("role", "general_user")
        tenant_id = app_metadata.get("tenant_id")
        
        # Map to UserToken model
        user_data = {
            **payload,
            "role": role,
            "tenant_id": tenant_id,
            "email": payload.get("email") or user_metadata.get("email")
        }
        
        return UserToken(**user_data)

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
