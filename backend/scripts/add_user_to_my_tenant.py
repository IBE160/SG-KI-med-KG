"""
Quick script to add a user to kjamtli@hotmail.com's tenant.
Usage: python add_user_to_my_tenant.py girlfriend@example.com
"""
import asyncio
import asyncpg
import json
import sys

DATABASE_URL = "postgresql://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"

# Your tenant ID (kjamtli@hotmail.com's tenant)
MY_TENANT_ID = "095b5d35-992e-482b-ac1b-d9ec10ac1425"


async def add_user_to_my_tenant(user_email: str):
    """Add a user to your tenant."""
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Check if user exists
        user_check = await conn.fetchrow("""
            SELECT u.id, u.email, u.tenant_id, u.role
            FROM public.user u
            WHERE u.email = $1
        """, user_email)

        if not user_check:
            print(f"ERROR: User {user_email} not found!")
            print("Make sure they have registered first.")
            return

        print(f"\nFound user: {user_check['email']}")
        print(f"  Current tenant: {user_check['tenant_id']}")
        print(f"  Current role: {user_check['role']}")

        if str(user_check['tenant_id']) == MY_TENANT_ID:
            print(f"\nUser is already in your tenant!")
            return

        print(f"\nMoving to tenant: {MY_TENANT_ID} (kjamtli@hotmail.com's tenant)")

        # Update public.user table
        await conn.execute("""
            UPDATE public.user
            SET tenant_id = $1
            WHERE email = $2
        """, MY_TENANT_ID, user_email)
        print("  OK Updated public.user table")

        # Update auth.users metadata
        auth_user = await conn.fetchrow("""
            SELECT id, raw_user_meta_data FROM auth.users WHERE email = $1
        """, user_email)

        if auth_user:
            metadata = auth_user['raw_user_meta_data']
            if isinstance(metadata, str):
                metadata = json.loads(metadata) if metadata else {}
            elif metadata is None:
                metadata = {}
            else:
                metadata = dict(metadata)

            metadata['tenant_id'] = MY_TENANT_ID
            metadata_json = json.dumps(metadata)

            await conn.execute("""
                UPDATE auth.users
                SET raw_user_meta_data = $1::jsonb
                WHERE id = $2
            """, metadata_json, auth_user['id'])
            print("  OK Updated auth.users metadata")

        # Verify
        verification = await conn.fetchrow("""
            SELECT u.email, u.tenant_id, au.raw_user_meta_data->>'tenant_id' as auth_tenant_id
            FROM public.user u
            JOIN auth.users au ON u.id = au.id
            WHERE u.email = $1
        """, user_email)

        print(f"\nVerification:")
        print(f"  App tenant: {verification['tenant_id']}")
        print(f"  Auth tenant: {verification['auth_tenant_id']}")

        if str(verification['tenant_id']) == verification['auth_tenant_id'] == MY_TENANT_ID:
            print(f"\nSUCCESS! {user_email} is now in your tenant.")
            print("They can log out and log back in to see your shared data.")
        else:
            print(f"\nWARNING: Tenant IDs don't match!")

    finally:
        await conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add_user_to_my_tenant.py <email>")
        print("Example: python add_user_to_my_tenant.py girlfriend@example.com")
        sys.exit(1)

    email = sys.argv[1]
    asyncio.run(add_user_to_my_tenant(email))
