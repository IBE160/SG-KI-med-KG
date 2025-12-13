"""
Script to sync admin@test.com role from auth metadata to application table.
"""
import asyncio
import asyncpg

DATABASE_URL = "postgresql://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"


async def sync_admin_role():
    """Sync admin@test.com role to 'admin' in public.user table."""
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Update admin@test.com role to admin
        result = await conn.execute("""
            UPDATE public.user
            SET role = 'admin'
            WHERE email = 'admin@test.com'
        """)
        print(f"Updated role: {result}")

        # Verify
        user = await conn.fetchrow("""
            SELECT u.email, u.role, au.raw_user_meta_data->>'role' as auth_role
            FROM public.user u
            JOIN auth.users au ON u.id = au.id
            WHERE u.email = 'admin@test.com'
        """)

        print(f"\nVerification for admin@test.com:")
        print(f"  Role (app): {user['role']}")
        print(f"  Role (auth): {user['auth_role']}")

        if user['role'] == user['auth_role']:
            print("  OK Roles match!")
        else:
            print("  WARNING: Roles still mismatch")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(sync_admin_role())
