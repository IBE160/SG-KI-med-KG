import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DB_URL = "postgresql+asyncpg://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"

async def drop_types():
    engine = create_async_engine(DB_URL, echo=True)
    async with engine.begin() as conn:
        print("Dropping types...")
        await conn.execute(text("DROP TYPE IF EXISTS suggestiontype CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS suggestionstatus CASCADE"))
        print("Types dropped.")

if __name__ == "__main__":
    asyncio.run(drop_types())