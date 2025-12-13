from uuid import UUID
import uuid
from fastapi import HTTPException, status
from gotrue.errors import AuthApiError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.supabase import get_supabase_client
from app.models.user import User
from app.schemas import UserCreate

class UserService:
    async def create_user(self, user_in: UserCreate, admin_user: User, db: AsyncSession) -> User:
        supabase = get_supabase_client()
        
        # Enforce tenant_id from admin
        # We ignore what comes in user_in.tenant_id if we want to strictly enforce it
        target_tenant_id = admin_user.tenant_id
        
        # Convert single role to list for new schema
        # TODO: Update UserCreate schema to support multiple roles directly
        roles = [user_in.role]
        
        # 1. Create in Supabase Auth
        try:
            # supabase.auth.admin.create_user is the correct method for server-side creation
            auth_response = supabase.auth.admin.create_user({
                "email": user_in.email,
                "password": user_in.password,
                "email_confirm": True, # Auto confirm since admin created it
                "user_metadata": {
                    "roles": roles, # Store as array in metadata
                    "tenant_id": str(target_tenant_id)
                }
            })
            auth_user = auth_response.user
            
        except AuthApiError as e:
            # Map Supabase errors to HTTP exceptions
            if "duplicate" in str(e).lower() or "already registered" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists"
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user in auth system: {str(e)}"
            )

        # 2. Create in public.users database
        try:
            db_user = User(
                id=uuid.UUID(auth_user.id),
                email=user_in.email,
                hashed_password="managed_by_supabase", # Placeholder as we use Supabase Auth
                is_active=True,
                is_superuser=user_in.role == "admin",
                is_verified=True,
                roles=roles, # Use roles array
                tenant_id=target_tenant_id
            )
            
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return db_user
            
        except Exception as e:
            # Cleanup: Attempt to delete the auth user if DB insertion fails
            try:
                supabase.auth.admin.delete_user(auth_user.id)
            except:
                pass # Best effort cleanup
                
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user record in database: {str(e)}"
            )

user_service = UserService()
