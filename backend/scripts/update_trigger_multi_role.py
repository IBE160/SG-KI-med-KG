"""
Script to update the handle_new_user trigger for multi-role support.
"""
import asyncio
import asyncpg

# Supabase connection details
DATABASE_URL = "postgresql://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"

# Target tenant (kjamtli@hotmail.com's tenant)
MAIN_TENANT_ID = "095b5d35-992e-482b-ac1b-d9ec10ac1425"

async def update_trigger_multi_role():
    """Update the handle_new_user trigger function to use roles array."""
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        print("Updating handle_new_user() trigger function for multi-role support...")
        
        # SQL from Story 2.5
        # Note: Changed 'role' to 'roles' and 'general_user' to ARRAY['general_user']
        sql = f"""
        CREATE OR REPLACE FUNCTION public.handle_new_user()
         RETURNS trigger AS $$
        DECLARE
          v_default_tenant_id UUID := '{MAIN_TENANT_ID}';
        BEGIN
          INSERT INTO public.user (
            id, email, hashed_password, is_active, is_superuser,
            is_verified, roles, tenant_id
          )
          VALUES (
            NEW.id,
            NEW.email,
            NEW.encrypted_password,
            COALESCE(NEW.email_confirmed_at IS NOT NULL, false),
            false,
            COALESCE(NEW.email_confirmed_at IS NOT NULL, false),
            ARRAY['general_user'],
            v_default_tenant_id
          );
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
        """
        
        await conn.execute(sql)
        print("SUCCESS: Trigger function updated successfully.")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(update_trigger_multi_role())
