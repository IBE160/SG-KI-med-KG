"""
Script to check how user creation works and what triggers tenant assignment.
"""
import asyncio
import asyncpg

DATABASE_URL = "postgresql://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"


async def check_user_creation():
    """Check database triggers and functions related to user creation."""
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Check for triggers on auth.users
        print("Checking for triggers on auth.users table:")
        print("="*60)
        triggers = await conn.fetch("""
            SELECT
                trigger_name,
                event_manipulation,
                event_object_table,
                action_statement,
                action_timing
            FROM information_schema.triggers
            WHERE event_object_table = 'users'
            AND event_object_schema = 'auth'
        """)

        if triggers:
            for trigger in triggers:
                print(f"\nTrigger: {trigger['trigger_name']}")
                print(f"  Event: {trigger['action_timing']} {trigger['event_manipulation']}")
                print(f"  Action: {trigger['action_statement']}")
        else:
            print("No triggers found on auth.users")

        # Check for functions that might handle user creation
        print("\n\n" + "="*60)
        print("Checking for user-related functions:")
        print("="*60)
        functions = await conn.fetch("""
            SELECT
                routine_name,
                routine_definition
            FROM information_schema.routines
            WHERE routine_schema = 'public'
            AND (
                routine_name LIKE '%user%'
                OR routine_name LIKE '%tenant%'
            )
            ORDER BY routine_name
        """)

        if functions:
            for func in functions:
                print(f"\nFunction: {func['routine_name']}")
                definition = func['routine_definition']
                if definition:
                    print(f"  Definition: {definition[:200]}...")
        else:
            print("No user/tenant-related functions found")

        # Check the user table schema
        print("\n\n" + "="*60)
        print("User table schema (tenant_id column):")
        print("="*60)
        schema = await conn.fetchrow("""
            SELECT
                column_name,
                data_type,
                column_default,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = 'user'
            AND column_name = 'tenant_id'
        """)

        if schema:
            print(f"\nColumn: {schema['column_name']}")
            print(f"  Type: {schema['data_type']}")
            print(f"  Default: {schema['column_default']}")
            print(f"  Nullable: {schema['is_nullable']}")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(check_user_creation())
