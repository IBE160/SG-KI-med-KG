# Story 2.4: Fix Default Tenant Assignment for New Users

Status: ready-for-dev

## Story

As a **system administrator**,
I want **all new user registrations to be assigned to a single default tenant instead of creating isolated tenants**,
so that **users can collaborate on the same organizational data without manual database interventions**.

## Acceptance Criteria

1. **Default Tenant Assignment**
   - When a new user registers via Supabase Auth, they are automatically assigned to a predefined default tenant.
   - The default tenant ID is: `095b5d35-992e-482b-ac1b-d9ec10ac1425` (kjamtli@hotmail.com's tenant).
   - No new tenant is created during user registration.
   - The `handle_new_user()` database trigger no longer generates random tenant IDs via `gen_random_uuid()`.

2. **Existing Users Consolidated**
   - All existing users in the database are consolidated into the default tenant.
   - Both `public.user` and `auth.users` tables reflect the same tenant_id.
   - The consolidation script (`backend/scripts/consolidate_tenant.py`) is executed before trigger modification.

3. **User Collaboration Verified**
   - Multiple users can log in and see the same compliance data (risks, controls, frameworks).
   - Row-Level Security (RLS) policies correctly filter data by the shared tenant_id.
   - No data isolation between users within the default tenant.

4. **Default Role Assignment**
   - New users are assigned the "general_user" role by default (existing behavior maintained).
   - Admins can still change user roles via the admin interface (Story 2.3 functionality preserved).

## Tasks / Subtasks

- [ ] **Database: Consolidate Existing Users** (AC: 2)
  - [ ] Run `backend/scripts/consolidate_tenant.py` to move all existing users to default tenant.
  - [ ] Verify all users have `tenant_id = 095b5d35-992e-482b-ac1b-d9ec10ac1425` in both tables.
  - [ ] Document the consolidation results (number of users updated).

- [ ] **Database: Modify Supabase Trigger** (AC: 1)
  - [ ] Update `handle_new_user()` function in Supabase SQL Editor.
  - [ ] Replace `gen_random_uuid()` with hardcoded default tenant UUID.
  - [ ] Remove tenant creation logic (no longer creates new tenants table entries if it exists).
  - [ ] Ensure trigger still assigns default role ("general_user").

- [ ] **Testing: User Registration Flow** (AC: 1, 3)
  - [ ] Create a new test user via the registration page.
  - [ ] Verify the user is assigned to the default tenant (`095b5d35...`).
  - [ ] Log in as the new user and verify they can see existing compliance data.
  - [ ] Verify no new tenant was created in the database.

- [ ] **Testing: Multi-User Collaboration** (AC: 3)
  - [ ] Log in as two different users (e.g., kjamtli@hotmail.com and test user).
  - [ ] Create a Risk as User 1.
  - [ ] Verify User 2 can see the same Risk in their dashboard.
  - [ ] Verify RLS policies correctly filter by shared tenant_id.

- [ ] **Testing: Verify Consolidation Script** (AC: 2)
  - [ ] Run `backend/scripts/consolidate_tenant.py` script.
  - [ ] Query database to verify all users have `tenant_id = 095b5d35-992e-482b-ac1b-d9ec10ac1425`.
  - [ ] Verify both `public.user` and `auth.users` tables are synchronized.
  - [ ] Document the consolidation results (number of users updated).

- [ ] **Testing: Verify Default Role Assignment** (AC: 4)
  - [ ] Create a new test user via registration page.
  - [ ] Verify the user is assigned "general_user" role by default.
  - [ ] Log in as admin and verify role change functionality still works (Story 2.3 preserved).
  - [ ] Verify trigger still sets `role = "general_user"` for new users.

- [ ] **Documentation: Update User Registration Guide** (AC: 1)
  - [ ] Update `docs/user-registration-guide.md` to reflect single-tenant behavior.
  - [ ] Remove references to multi-tenant isolation for MVP.
  - [ ] Add note about future invitation system (post-MVP).

## Dev Notes

### Architecture Patterns

- **Single-Tenant MVP**: For the school project and MVP, a single shared tenant is sufficient. Multi-tenancy will be implemented post-MVP via the invitation system described in `docs/tenant-management-design.md`.
- **Trigger Modification**: The `handle_new_user()` trigger exists in Supabase, not in local code. Changes must be made via the Supabase SQL Editor in the web console.
- **No Docker Dependency**: This is a Supabase-hosted database change. Docker local environment is not relevant for MVP deployment.

### Source Tree Components

- `backend/scripts/consolidate_tenant.py` (Existing - run this first)
- Supabase Database Trigger: `handle_new_user()` (Modify via SQL Editor)
- `docs/user-registration-guide.md` (Update)

### Testing Standards

- **Integration Test**: Create a new user via the frontend and verify tenant assignment in the database.
- **Manual Test**: Register two users and verify they can collaborate on the same data.
- **Database Query**: Verify all users have the same `tenant_id` after consolidation.

### Project Structure Notes

**Alignment:**
- Single-tenant approach simplifies MVP development and testing.
- Aligns with current Supabase RLS policies (filter by `tenant_id`).

**Conflicts:** None detected.

### Learnings from Previous Stories

**From Story 2-1 (User Registration & Login):**
- The `handle_new_user()` trigger creates a `public.user` record when a new user registers via Supabase Auth.
- The trigger currently generates a unique tenant for each user, causing isolation.

**From Story 2-3 (Admin User Creation - Status: done):**
- **New Components Created:**
  - `backend/app/services/user_service.py` - User creation service logic with Supabase Admin API integration
  - `backend/app/api/v1/endpoints/users.py` - POST /users endpoint for admin user creation
  - `backend/tests/api/v1/test_create_user.py` - Tests for user creation endpoint
  - `frontend/components/admin/CreateUserDialog.tsx` - User creation UI dialog
  - `frontend/app/dashboard/admin/users/page.tsx` - Updated with Create User button
- **Completion Notes:**
  - `createUser` function in `clientService.ts` was deferred pending client regeneration (requires `npm run generate-client`)
  - JWT Secret issue in tests resolved by overriding `get_current_active_user` dependency with mocks
- **Context for This Story:**
  - Admins can assign roles, but tenant assignment is fixed at registration time via the trigger
  - This story ensures all users share the same tenant from the start, enabling collaboration

[Source: docs/sprint-artifacts/2-3-admin-user-creation-role-assignment.md]

### Current Trigger Function (To Be Modified)

**Current behavior (from `docs/tenant-management-design.md`):**
```sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
 RETURNS trigger AS $$
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
    gen_random_uuid()  -- ❌ THIS CREATES A NEW TENANT PER USER
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

**Required change:**
```sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
 RETURNS trigger AS $$
DECLARE
  v_default_tenant_id UUID := '095b5d35-992e-482b-ac1b-d9ec10ac1425';
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
    v_default_tenant_id  -- ✅ USE DEFAULT TENANT
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### References

- [Epic 2 Tech Spec](docs/sprint-artifacts/tech-spec-epic-2.md) - Story 2.4 ACs 9-12 (tenant consolidation requirements)
- [Epic 2: User Identity & Access Management](docs/epics.md#epic-2-user-identity--access-management-iam) - Parent epic context for IAM
- [Product Requirements Document](docs/PRD.md) - Multi-tenancy architecture and RBAC requirements
- [System Architecture](docs/architecture.md) - Supabase Auth patterns, RLS policies, and multi-tenant architecture
- [Tenant Management Design](docs/tenant-management-design.md) - Full analysis of the multi-tenant issue and proposed solution
- [Story 2.1: User Registration & Login](docs/sprint-artifacts/2-1-implement-user-registration-login-email-password.md) - Original registration implementation
- [Story 2.3: Admin User Creation](docs/sprint-artifacts/2-3-admin-user-creation-role-assignment.md) - Role management context

## Dev Agent Record

### Context Reference

- docs/sprint-artifacts/2-4-fix-default-tenant-assignment.context.xml

### Agent Model Used

<!-- Will be filled during development -->

### Debug Log References

<!-- Will be filled during development -->

### Completion Notes List

<!-- Will be filled during development -->

### File List

<!-- Will be filled during development -->

## Change Log

**2025-12-13** - Story drafted by Bob (Scrum Master). Critical fix for tenant isolation issue discovered during testing.
