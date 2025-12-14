import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
from sqlalchemy.future import select
from app.models.compliance import Control
from uuid import UUID

# Force correct DB URL for local Supabase connection
DB_URL = "postgresql+asyncpg://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"

CONTROL_ID = "c99ee76e-603a-4a8e-a722-b335a818c494"
CORRECT_OWNER_ID = "07e03936-d6e1-4793-b5ca-539adbf03aa7" # gro.furseth@gmail.com

async def correct_owner():
    print(f"Connecting to: {DB_URL}")
    engine = create_async_engine(DB_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print(f"Correcting Control {CONTROL_ID} Owner to {CORRECT_OWNER_ID}...")
        
        stmt = (
            update(Control)
            .where(Control.id == UUID(CONTROL_ID))
            .values(owner_id=UUID(CORRECT_OWNER_ID))
        )
        
        await session.execute(stmt)
        await session.commit()
        
        # Verify
        result = await session.execute(select(Control).where(Control.id == UUID(CONTROL_ID)))
        control = result.scalar_one()
        print(f"Correction Complete. Control '{control.name}' Owner: {control.owner_id}")

if __name__ == "__main__":
    asyncio.run(correct_owner())