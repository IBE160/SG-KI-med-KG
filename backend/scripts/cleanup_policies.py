"""
Clean up old RLS policies on regulatory_frameworks.
"""
import asyncio
import asyncpg

DATABASE_URL = "postgresql://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"

async def cleanup_policies():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        print("Dropping old policies on regulatory_frameworks...")
        policies = [
            "tenant_isolation_select_regulatory_frameworks",
            "tenant_isolation_insert_regulatory_frameworks",
            "tenant_isolation_update_regulatory_frameworks",
            "tenant_isolation_delete_regulatory_frameworks"
        ]
        
        for p in policies:
            print(f"Dropping {p}...")
            await conn.execute(f'DROP POLICY IF EXISTS "{p}" ON regulatory_frameworks')
            
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(cleanup_policies())
