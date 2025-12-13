"""
Script to show the full handle_new_user trigger function.
"""
import asyncio
import asyncpg

DATABASE_URL = "postgresql://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"


async def show_trigger_function():
    """Show the full handle_new_user function."""
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Get the full function definition
        function_def = await conn.fetchrow("""
            SELECT pg_get_functiondef(oid) as definition
            FROM pg_proc
            WHERE proname = 'handle_new_user'
        """)

        if function_def:
            print("="*70)
            print("FULL HANDLE_NEW_USER FUNCTION DEFINITION:")
            print("="*70)
            print(function_def['definition'])
            print("="*70)
        else:
            print("Function 'handle_new_user' not found")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(show_trigger_function())
