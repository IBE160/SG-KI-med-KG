"""
List tables.
"""
import asyncio
import asyncpg

DATABASE_URL = "postgresql://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"

async def list_tables():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        rows = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        print("Tables in public schema:")
        for row in rows:
            print(f"  - {row['tablename']}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(list_tables())
