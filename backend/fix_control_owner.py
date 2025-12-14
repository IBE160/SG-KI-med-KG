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
OWNER_ID = "555f8e27-0ee5-4552-8583-59da03cb3d48" # bpo@test.no

async def fix_owner():
    print(f"Connecting to: {DB_URL}")
    engine = create_async_engine(DB_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print(f"Updating Control {CONTROL_ID} with Owner {OWNER_ID}...")
        
        stmt = (
            update(Control)
            .where(Control.id == UUID(CONTROL_ID))
            .values(owner_id=UUID(OWNER_ID))
        )
        
        await session.execute(stmt)
        await session.commit()
        
        # Verify
        result = await session.execute(select(Control).where(Control.id == UUID(CONTROL_ID)))
        control = result.scalar_one()
        print(f"Update Complete. Control '{control.name}' Owner: {control.owner_id}")

if __name__ == "__main__":
    asyncio.run(fix_owner())