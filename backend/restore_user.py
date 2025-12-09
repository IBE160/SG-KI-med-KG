import asyncio
import uuid
from uuid import UUID
from app.core.supabase import get_supabase_client
from app.database import engine
from app.models.user import User
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select

async def restore_user(email: str, role: str = "general"):
    print(f"Restoring user {email}...")
    
    # 1. Fetch from Supabase
    try:
        supabase = get_supabase_client()
        # Fetch users
        response = supabase.auth.admin.list_users()
        # response can be a UserResponse object or list depending on version
        # recent supabase-py: response has .users which is the list
        users = response.users if hasattr(response, 'users') else response
        
        target_user = next((u for u in users if u.email == email), None)
        
        if not target_user:
            print(f"❌ User {email} not found in Supabase Auth!")
            return
            
        print(f"Found in Supabase: ID={target_user.id}")
        user_id = UUID(target_user.id)
        
    except Exception as e:
        print(f"❌ Error communicating with Supabase: {e}")
        return

    # 2. Check local DB
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(select(User).filter(User.email == email))
        existing_user = result.scalars().first()
        
        if existing_user:
            print(f"⚠️ User {email} already exists in local DB. Updating role...")
            existing_user.role = role
            await session.commit()
            print("✅ User updated.")
            return

        # 3. Insert into local DB
        # Reuse tenant_id from an existing admin if possible, else generate new
        admin_result = await session.execute(select(User).filter(User.role == "admin"))
        admin_user = admin_result.scalars().first()
        tenant_id = admin_user.tenant_id if admin_user else uuid.uuid4()
        
        print(f"Using tenant_id: {tenant_id}")

        new_user = User(
            id=user_id,
            email=email,
            # We don't have the password hash, but for Supabase Auth integration, 
            # the backend primarily uses the ID. 
            # However, if the User model requires hashed_password (non-nullable), we provide a dummy.
            hashed_password="$argon2id$v=19$m=65536,t=3,p=4$dummyhash$dummyhash", 
            is_active=True,
            is_superuser=False,
            is_verified=True,
            role=role,
            tenant_id=tenant_id
        )
        
        session.add(new_user)
        try:
            await session.commit()
            print(f"✅ User {email} restored to local DB with role '{role}'!")
        except Exception as e:
            print(f"❌ Error inserting user: {e}")

if __name__ == "__main__":
    asyncio.run(restore_user("kjamtli@hotmail.com", "general"))
