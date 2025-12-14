import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.models.compliance import Control
from app.models.suggestion import AISuggestion
from app.models.user import User

# Force correct DB URL for local Supabase connection
DB_URL = "postgresql+asyncpg://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"

async def check_data_state():
    print(f"Connecting to: {DB_URL}")
    engine = create_async_engine(DB_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 1. Check AI Suggestions
        print("\n--- AI Suggestions ---")
        result = await session.execute(select(AISuggestion))
        suggestions = result.scalars().all()
        print(f"Count: {len(suggestions)}")
        for s in suggestions:
            print(f" - {s.id} | {s.content.get('name')} | Status: {s.status}")

        # 2. Check Controls
        print("\n--- Controls ---")
        result = await session.execute(select(Control))
        controls = result.scalars().all()
        print(f"Count: {len(controls)}")
        for c in controls:
            print(f" - {c.name} (ID: {c.id})")
            print(f"   Tenant: {c.tenant_id}")
            print(f"   Owner: {c.owner_id}")
            
            # Fetch Owner Name
            if c.owner_id:
                user_res = await session.execute(select(User).where(User.id == c.owner_id))
                u = user_res.scalar_one_or_none()
                print(f"   Owner Email: {u.email if u else 'UNKNOWN'}")

if __name__ == "__main__":
    asyncio.run(check_data_state())
