"""
Script to test the handle_new_user trigger logic.
"""
import asyncio
import asyncpg
import uuid

# Supabase connection details
DATABASE_URL = "postgresql://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"

# Target tenant (kjamtli@hotmail.com's tenant)
MAIN_TENANT_ID = "095b5d35-992e-482b-ac1b-d9ec10ac1425"

async def test_trigger():
    """Test the trigger by inserting a user into auth.users."""
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    test_id = str(uuid.uuid4())
    test_email = f"trigger_test_{{test_id[:8]}}@example.com"
    
    try:
        print(f"Testing trigger with user: {{test_email}} ({{test_id}})")
        
        # 1. Insert into auth.users
        print("Inserting into auth.users...")
        # Note: minimal columns needed for trigger
        await conn.execute("""
            INSERT INTO auth.users (id, email, encrypted_password, email_confirmed_at)
            VALUES ($1, $2, 'hashed_pass', now())
        """, test_id, test_email)
        
        # 2. Check public.user
        print("Checking public.user...")
        row = await conn.fetchrow("SELECT * FROM public.user WHERE id = $1", test_id)
        
        if not row:
            print("❌ FAILURE: No user found in public.user! Trigger might not have fired.")
            return

        print(f"User found: {row['email']}")
        print(f"  Tenant ID: {row['tenant_id']}")
        print(f"  Role: {row['role']}")
        
        # 3. Verify assertions
        assert str(row['tenant_id']) == MAIN_TENANT_ID, f"Tenant ID mismatch! Expected {MAIN_TENANT_ID}, got {row['tenant_id']}"
        assert row['role'] == "general_user", f"Role mismatch! Expected 'general_user', got {row['role']}"
        
        print("✅ SUCCESS: Trigger worked correctly!")
        print("  - User created in public.user")
        print("  - Tenant ID assigned to default")
        print("  - Default role assigned")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise
    finally:
        # 4. Cleanup
        print("\nCleaning up...")
        await conn.execute("DELETE FROM auth.users WHERE id = $1", test_id)
        # public.user should be deleted by cascade usually, or we delete it manually if needed.
        # But auth.users is the source.
        await conn.close()

if __name__ == "__main__":
    asyncio.run(test_trigger())
