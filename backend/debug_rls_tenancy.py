import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.config import settings

# Use the direct DB URL
DB_URL = "postgresql+asyncpg://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"

async def check_rls_and_tenancy():
    engine = create_async_engine(DB_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("--- 1. Checking RLS Policies on 'controls' table ---")
        result = await session.execute(text("select * from pg_policies where tablename = 'controls';"))
        policies = result.all()
        if not policies:
            print("No RLS policies found on 'controls'. (Table might be public or RLS disabled)")
        for p in policies:
            print(f"Policy: {p.policyname} | Cmd: {p.cmd} | Roles: {p.roles} | Using: {p.qual} | Check: {p.with_check}")

        print("\n--- 2. Checking RLS Enablement ---")
        result = await session.execute(text("select relname, relrowsecurity from pg_class where relname = 'controls';"))
        row = result.fetchone()
        print(f"Table: {row[0]}, RLS Enabled: {row[1]}")

        print("\n--- 3. Checking Data Alignment ---")
        # Get the control
        result = await session.execute(text("select id, name, tenant_id, owner_id from controls where name = 'Whistleblowing'"))
        control = result.fetchone()
        
        if control:
            print(f"Control: {control.name}")
            print(f"  ID: {control.id}")
            print(f"  Tenant: {control.tenant_id}")
            print(f"  Owner: {control.owner_id}")
            
            # Get the Owner User
            if control.owner_id:
                result = await session.execute(text(f"select id, email, tenant_id from \"user\" where id = '{control.owner_id}'"))
                user = result.fetchone()
                if user:
                    print(f"Owner User: {user.email}")
                    print(f"  ID: {user.id}")
                    print(f"  Tenant: {user.tenant_id}")
                    
                    if str(user.tenant_id) == str(control.tenant_id):
                        print("  ✅ Tenant IDs match.")
                    else:
                        print(f"  ❌ TENANT ID MISMATCH! User: {user.tenant_id} vs Control: {control.tenant_id}")
                else:
                    print("  ❌ Owner User NOT FOUND in DB!")
        else:
            print("Control 'Whistleblowing' not found.")

if __name__ == "__main__":
    asyncio.run(check_rls_and_tenancy())
