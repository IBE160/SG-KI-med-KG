"""
Script to update the handle_new_user trigger in Supabase.
This replaces the random tenant generation with a fixed default tenant.
"""
import asyncio
import asyncpg

# Supabase connection details
DATABASE_URL = "postgresql://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"

# Target tenant (kjamtli@hotmail.com's tenant)
MAIN_TENANT_ID = "095b5d35-992e-482b-ac1b-d9ec10ac1425"

async def update_trigger():
    """Update the handle_new_user trigger function."""
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        print("Updating handle_new_user() trigger function...")
        
        # SQL from Story 2.4
        sql = f"""
        CREATE OR REPLACE FUNCTION public.handle_new_user()
         RETURNS trigger AS $$
        DECLARE
          v_default_tenant_id UUID := '{MAIN_TENANT_ID}';
        BEGIN
          INSERT INTO public.user (
            id, email, hashed_password, is_active, is_superuser,
            is_verified, role, tenant_id
          )
          VALUES (
            NEW.id,
            NEW.email,
            NEW.encrypted_password,
            COALESCE(NEW.email_confirmed_at IS NOT NULL, false),
            false,
            COALESCE(NEW.email_confirmed_at IS NOT NULL, false),
            'general_user',
            v_default_tenant_id
          );
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
        """
        
        await conn.execute(sql)
        print("SUCCESS: Trigger function updated successfully.")
        print(f"New users will now be assigned to tenant: {MAIN_TENANT_ID}")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(update_trigger())
