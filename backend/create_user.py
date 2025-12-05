import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models import User
from fastapi_users.password import PasswordHelper
import uuid

# Use the same database URL as dev-start-backend.ps1
DATABASE_URL = "sqlite+aiosqlite:///./dev.db"

async def create_admin_user():
    engine = create_async_engine(DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # Check if user exists
        # (Simplified check, in a real app use the repository/manager)
        # For this quick script, we'll just try to insert and ignore error if exists
        
        password_helper = PasswordHelper()
        hashed_password = password_helper.hash("Admin123!")
        
        new_user = User(
            id=uuid.uuid4(),
            email="admin@example.com",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=True,
            is_verified=True
        )
        
        session.add(new_user)
        try:
            await session.commit()
            print("✅ User created successfully!")
            print("Email: admin@example.com")
            print("Password: Admin123!")
        except Exception as e:
            print(f"⚠️  User might already exist or error occurred: {e}")

    await engine.dispose()

if __name__ == "__main__":
    print("Creating admin user...")
    asyncio.run(create_admin_user())
