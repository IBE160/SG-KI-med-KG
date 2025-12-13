"""
Inspect RLS policies for relevant tables.
"""
import asyncio
import asyncpg

DATABASE_URL = "postgresql://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"

async def inspect_policies():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        tables = ['risks', 'controls', 'regulatory_frameworks']
        for table in tables:
            print(f"\nPolicies for table: {table}")
            policies = await conn.fetch("SELECT policyname, cmd, qual, with_check FROM pg_policies WHERE tablename = $1", table)
            for p in policies:
                print(f"  - Name: {p['policyname']}")
                print(f"    Command: {p['cmd']}")
                print(f"    Using: {p['qual']}")
                print(f"    With Check: {p['with_check']}")
                
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(inspect_policies())