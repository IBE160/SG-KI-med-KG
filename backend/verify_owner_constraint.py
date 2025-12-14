import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from app.models.compliance import Control, Risk, BusinessProcess
from uuid import uuid4

# Force correct DB URL for local Supabase connection
DB_URL = "postgresql+asyncpg://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"

async def verify_constraints():
    print(f"Connecting to: {DB_URL}")
    engine = create_async_engine(DB_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("\n--- Verifying Owner Constraint on Controls ---")
        try:
            # Attempt to create a Control WITHOUT an owner
            control = Control(
                name="Test Control No Owner",
                description="This should fail",
                tenant_id=uuid4(),
                owner_id=None # EXPLICITLY NONE
            )
            session.add(control)
            await session.commit()
            print("❌ FAILED: Successfully created a Control without an owner. Constraint is NOT active.")
        except IntegrityError as e:
            print("✅ SUCCESS: Caught expected IntegrityError. Constraint IS active.")
            print(f"   Error detail: {e.orig}")
            await session.rollback()
        except Exception as e:
            print(f"⚠️ Unexpected error: {type(e).__name__}: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(verify_constraints())
