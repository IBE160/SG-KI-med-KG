"""
Script to verify all users are in the same tenant with correct roles.
"""
import asyncio
import asyncpg

DATABASE_URL = "postgresql://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"


async def verify_users():
    """Display all user information for verification."""
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        users = await conn.fetch("""
            SELECT
                u.email,
                u.role,
                u.tenant_id,
                au.raw_user_meta_data->>'role' as auth_role,
                au.raw_user_meta_data->>'tenant_id' as auth_tenant_id
            FROM public.user u
            JOIN auth.users au ON u.id = au.id
            ORDER BY u.email
        """)

        print("\n" + "="*70)
        print("USER VERIFICATION REPORT")
        print("="*70)

        tenant_ids = set()
        for user in users:
            print(f"\nEmail: {user['email']}")
            print(f"  Role (app):     {user['role']}")
            print(f"  Role (auth):    {user['auth_role']}")
            print(f"  Tenant (app):   {user['tenant_id']}")
            print(f"  Tenant (auth):  {user['auth_tenant_id']}")

            # Collect unique tenant IDs
            tenant_ids.add(str(user['tenant_id']))

            # Check for mismatches
            mismatches = []
            if user['role'] != user['auth_role']:
                mismatches.append("role mismatch")
            if str(user['tenant_id']) != user['auth_tenant_id']:
                mismatches.append("tenant mismatch")

            if mismatches:
                print(f"  Status: WARNING - {', '.join(mismatches)}")
            else:
                print(f"  Status: OK")

        print("\n" + "="*70)
        print(f"Total users: {len(users)}")
        print(f"Unique tenants: {len(tenant_ids)}")
        if len(tenant_ids) == 1:
            print(f"SUCCESS: All users consolidated to tenant: {tenant_ids.pop()}")
        else:
            print(f"WARNING: Users span multiple tenants: {tenant_ids}")
        print("="*70 + "\n")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(verify_users())
