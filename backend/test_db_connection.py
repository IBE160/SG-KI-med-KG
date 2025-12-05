import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Hardcoded Direct Connection String
# Using postgresql+asyncpg driver
DB_URL = "postgresql+asyncpg://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"


async def test_connection():
    print(f"Connecting to {DB_URL.split('@')[1]}...")
    try:
        engine = create_async_engine(DB_URL, echo=False)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"Success! Result: {result.scalar()}")
    except Exception as e:
        print(f"Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_connection())
