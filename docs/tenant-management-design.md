# Tenant Management Design

## Current State (Problem)

Every user registration creates a **new isolated tenant** via the database trigger:

```sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
...
    VALUES (
      ...
      gen_random_uuid()  -- Each user gets their own tenant!
    );
```

**Result:** Users cannot collaborate - they're all in separate data silos.

## Proposed Solution: Tenant Invitation System

### Architecture Changes

#### 1. New Database Tables

```sql
-- Table to store tenant information
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES public.user(id)
);

-- Table to store invitations
CREATE TABLE tenant_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    invited_by UUID NOT NULL REFERENCES public.user(id),
    invitation_code VARCHAR(50) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_active_invitation UNIQUE (tenant_id, email, used_at)
);
```

#### 2. Modified Registration Flow

**Option A: Registration with Invitation Code**
```
1. User receives invitation email with link: /register?code=ABC123
2. Registration form pre-fills email and includes hidden invitation code
3. On submit, backend:
   - Validates invitation code
   - Creates user in auth.users
   - Trigger creates user in public.user with INVITED tenant_id (not random)
   - Marks invitation as used
```

**Option B: First User Creates Tenant**
```
1. First user registers (creates new tenant automatically)
2. Becomes admin of that tenant
3. Can invite others to join
```

#### 3. Updated Trigger Function

```sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
AS $function$
  DECLARE
    v_tenant_id UUID;
    v_role VARCHAR(50);
    v_invitation RECORD;
  BEGIN
    -- Check if user was invited
    SELECT tenant_id, tenant_invitations.id
    INTO v_invitation
    FROM tenant_invitations
    WHERE email = NEW.email
      AND used_at IS NULL
      AND expires_at > NOW()
    ORDER BY created_at DESC
    LIMIT 1;

    IF FOUND THEN
      -- User was invited - use invitation's tenant
      v_tenant_id := v_invitation.tenant_id;
      v_role := 'general_user';  -- Or get from invitation

      -- Mark invitation as used
      UPDATE tenant_invitations
      SET used_at = NOW()
      WHERE id = v_invitation.id;
    ELSE
      -- New tenant - this user is creating their own organization
      -- First create the tenant
      INSERT INTO tenants (name, created_by)
      VALUES (NEW.email || '''s Organization', NEW.id)
      RETURNING id INTO v_tenant_id;

      -- First user becomes admin
      v_role := 'admin';
    END IF;

    -- Create user record
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
      v_role,
      v_tenant_id
    );

    RETURN NEW;
  END;
$function$;
```

### User Flows

#### Flow 1: Starting a New Organization (You)
1. Go to `/register`
2. Enter email and password
3. System creates:
   - Your user account
   - A new tenant (organization)
   - Makes you admin
4. You can now invite your girlfriend

#### Flow 2: Joining via Invitation (Your Girlfriend)
1. You (as admin) go to Settings > Team Management
2. Click "Invite Team Member"
3. Enter her email address
4. System sends her an email with invitation link
5. She clicks the link → goes to `/register?code=ABC123`
6. She creates her account
7. Automatically added to YOUR tenant

### UI Components Needed

1. **Tenant Settings Page** (`/dashboard/settings/organization`)
   - View tenant name
   - Manage team members
   - Send invitations

2. **Team Management Component**
   - List all users in tenant
   - Send new invitations
   - Revoke unused invitations
   - Remove users (for admins only)

3. **Modified Registration Page**
   - Detect invitation code in URL
   - Show "You're joining [Organization Name]" message
   - Validate invitation before allowing registration

### API Endpoints Needed

```typescript
POST   /api/v1/invitations          // Create invitation (admin only)
GET    /api/v1/invitations          // List invitations (admin only)
DELETE /api/v1/invitations/{id}     // Revoke invitation (admin only)
GET    /api/v1/invitations/validate/{code}  // Validate invitation code
GET    /api/v1/tenant               // Get current tenant info
PUT    /api/v1/tenant               // Update tenant settings (admin only)
GET    /api/v1/tenant/members       // List tenant members
DELETE /api/v1/tenant/members/{id}  // Remove member (admin only)
```

## Quick Fix for You and Your Girlfriend (Today)

Since implementing the full invitation system takes time, here's how to work together NOW:

### Method 1: Share One Account
Both log in as `kjamtli@hotmail.com` - you'll see the same data but can't distinguish who did what.

### Method 2: Manual Assignment
1. Your girlfriend registers her own account
2. Note her email address
3. Run this script to add her to your tenant:

```python
# add_user_to_tenant.py
import asyncio
import asyncpg

DATABASE_URL = "postgresql://postgres:qsgcFcsunjkjKPLv@db.xjltxcwdbvsuxyuffzmt.supabase.co:5432/postgres"

async def add_user_to_tenant(user_email: str, target_tenant_id: str):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Update both tables
        await conn.execute("""
            UPDATE public.user
            SET tenant_id = $1
            WHERE email = $2
        """, target_tenant_id, user_email)

        # Update auth metadata
        user = await conn.fetchrow("""
            SELECT id, raw_user_meta_data FROM auth.users WHERE email = $1
        """, user_email)

        if user:
            metadata = dict(user['raw_user_meta_data'] or {})
            metadata['tenant_id'] = target_tenant_id

            await conn.execute("""
                UPDATE auth.users
                SET raw_user_meta_data = $1::jsonb
                WHERE id = $2
            """, json.dumps(metadata), user['id'])

        print(f"Added {user_email} to tenant {target_tenant_id}")
    finally:
        await conn.close()

# Usage:
# asyncio.run(add_user_to_tenant(
#     "girlfriend@example.com",
#     "095b5d35-992e-482b-ac1b-d9ec10ac1425"  # Your tenant ID
# ))
```

## Summary

**Current behavior:** Each registration = new isolated tenant (can't collaborate)

**Your options:**
1. **Quick:** Share login credentials
2. **Manual:** Register separately, then manually assign to same tenant via database
3. **Proper:** Implement tenant invitation system (requires development)

**Important:** Tenant is NOT related to:
- Your computer
- Your network
- Your git repository
- Whether you're "up to date" with git pull

It's purely a **database-level isolation mechanism** that's assigned when the user account is created.
