import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.models.compliance import Control
from app.models.user import User

# Force correct DB URL for local Supabase connection
# Use the one seen in .env: postgresql+asyncpg://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres
DB_URL = "postgresql+asyncpg://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"

async def list_controls():
    print(f"Connecting to: {DB_URL}")
    engine = create_async_engine(DB_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Fetch all controls
        print("Fetching controls...")
        result = await session.execute(select(Control))
        controls = result.scalars().all()
        
        print(f"Total Controls found: {len(controls)}")
        for c in controls:
            print(f"Control: {c.name} (ID: {c.id})")
            print(f"  Tenant: {c.tenant_id}")
            print(f"  Owner: {c.owner_id}")
            
        # Fetch users to correlate owner IDs
        print("\nFetching users...")
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"Total Users: {len(users)}")
        for u in users:
            print(f"User: {u.email} (ID: {u.id})")
            print(f"  Tenant: {u.tenant_id}")
            # print(f"  Roles: {u.roles}") # Roles might be a property or column, check model

if __name__ == "__main__":
    asyncio.run(list_controls())
