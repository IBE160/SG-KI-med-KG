"""Create admin user in database."""
import asyncio
import uuid
from sqlalchemy import text
from app.database import get_async_session
import bcrypt


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def create_admin_user():
    """Create admin user kjamtli@hotmail.com."""
    email = "kjamtli@hotmail.com"
    password = "test123"  # Change this to your desired password
    hashed_password = hash_password(password)
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()

    async for session in get_async_session():
        # Check if user exists
        result = await session.execute(
            text("SELECT id FROM user WHERE email = :email"),
            {"email": email}
        )
        existing = result.fetchone()

        if existing:
            print(f"User {email} already exists")
            return

        # Insert admin user
        await session.execute(
            text("""
                INSERT INTO user (id, email, hashed_password, is_active, is_superuser, is_verified, role, tenant_id)
                VALUES (:id, :email, :hashed_password, :is_active, :is_superuser, :is_verified, :role, :tenant_id)
            """),
            {
                "id": str(user_id),
                "email": email,
                "hashed_password": hashed_password,
                "is_active": True,
                "is_superuser": True,
                "is_verified": True,
                "role": "admin",
                "tenant_id": str(tenant_id)
            }
        )
        await session.commit()
        print(f"Admin user created: {email}")
        print(f"Password: {password}")
        print(f"Tenant ID: {tenant_id}")
        break


if __name__ == "__main__":
    asyncio.run(create_admin_user())
