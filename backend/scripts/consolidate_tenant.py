"""
Script to consolidate all test users into a single tenant.
Updates both public.user and auth.users tables.
"""
import asyncio
import asyncpg
import json
from uuid import UUID

# Supabase connection details
DATABASE_URL = "postgresql://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"

# Target tenant (kjamtli@hotmail.com's tenant)
MAIN_TENANT_ID = "095b5d35-992e-482b-ac1b-d9ec10ac1425"


async def consolidate_tenants():
    """Consolidate all users into the main tenant."""

    # Connect directly with asyncpg for better control
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # 1. Update public.user table
        print("Updating public.user table...")
        result = await conn.execute("""
            UPDATE public.user
            SET tenant_id = $1
        """, UUID(MAIN_TENANT_ID))
        print(f"Updated public.user: {result}")

        # 2. Update auth.users metadata - using proper JSON construction
        print("\nUpdating auth.users metadata...")

        # Get all users from auth.users
        users = await conn.fetch("SELECT id, email, raw_user_meta_data FROM auth.users")
        print(f"Found {len(users)} users in auth.users")

        # Update each user's metadata
        for user in users:
            user_id = user['id']
            email = user['email']
            current_metadata = user['raw_user_meta_data']

            # Convert to dict if it's a string (shouldn't happen but be safe)
            if isinstance(current_metadata, str):
                current_metadata = json.loads(current_metadata) if current_metadata else {}
            elif current_metadata is None:
                current_metadata = {}
            else:
                # Make a copy to avoid modifying the original
                current_metadata = dict(current_metadata)

            # Update tenant_id in metadata
            current_metadata['tenant_id'] = MAIN_TENANT_ID

            # Convert dict to JSON string for asyncpg
            metadata_json = json.dumps(current_metadata)

            # Use jsonb parameter binding with JSON string
            await conn.execute("""
                UPDATE auth.users
                SET raw_user_meta_data = $1::jsonb
                WHERE id = $2
            """, metadata_json, user_id)

            print(f"  OK Updated {email} (id: {user_id})")

        # 3. Verify the updates
        print("\n" + "="*60)
        print("VERIFICATION - Users after consolidation:")
        print("="*60)

        verification = await conn.fetch("""
            SELECT
                u.email,
                u.role,
                u.tenant_id as app_tenant_id,
                au.raw_user_meta_data->>'tenant_id' as auth_tenant_id,
                au.raw_user_meta_data->>'role' as auth_role
            FROM public.user u
            JOIN auth.users au ON u.id = au.id
            ORDER BY u.email
        """)

        for row in verification:
            print(f"\nEmail: {row['email']}")
            print(f"  Role (app): {row['role']}")
            print(f"  Role (auth): {row['auth_role']}")
            print(f"  Tenant ID (app): {row['app_tenant_id']}")
            print(f"  Tenant ID (auth): {row['auth_tenant_id']}")

            # Check for mismatches
            if str(row['app_tenant_id']) != row['auth_tenant_id']:
                print(f"  WARNING: Tenant ID mismatch!")
            else:
                print(f"  OK Tenant IDs match")

        print("\n" + "="*60)
        print("SUCCESS: Tenant consolidation complete!")
        print(f"All users now belong to tenant: {MAIN_TENANT_ID}")
        print("="*60)

    except Exception as e:
        print(f"\nERROR: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(consolidate_tenants())
