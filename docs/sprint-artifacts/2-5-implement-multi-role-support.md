# Story 2.5: Implement Multi-Role Support for Non-General Users

Status: ready-for-dev

## Story

As an **Admin**,
I want **to assign multiple roles (admin, bpo, executive) to a single user**,
so that **users with overlapping responsibilities can perform multiple functions without switching accounts, while ensuring general_user remains a distinct, entry-level role**.

## Acceptance Criteria

1. **Multi-Role Assignment for Non-General Users**
   - A user can be assigned multiple roles from: admin, bpo, executive.
   - Valid combinations: `["admin"]`, `["bpo"]`, `["admin", "bpo"]`, `["admin", "executive"]`, `["bpo", "executive"]`, `["admin", "bpo", "executive"]`.
   - The `general_user` role is mutually exclusive with all other roles.
   - If a user has `general_user`, they cannot have any additional roles.
   - If a user has any other role(s), they cannot have `general_user`.

2. **Backend RBAC Updated**
   - The `has_role()` dependency checks if the user has ANY of the required roles (OR logic, not AND).
   - Example: `has_role(["admin", "bpo"])` passes if user has `["admin"]`, `["bpo"]`, or `["admin", "bpo"]`.
   - All existing endpoint protections continue to work correctly with the new multi-role logic.
   - API endpoints validate role combinations (reject `["general_user", "admin"]`).

3. **Database Schema Refactored**
   - The `user.role` column is changed from `String(50)` to `ARRAY` (PostgreSQL) or a junction table `user_roles`.
   - Existing single-role users are migrated to the new multi-role format via Alembic migration.
   - Example: `role = "admin"` → `roles = ["admin"]`.
   - Supabase `handle_new_user()` trigger assigns `roles = ["general_user"]` by default.

4. **Frontend Multi-Role UI**
   - Admin User Management page displays multiple role badges per user.
   - Role assignment dialog uses a multi-select dropdown (checkboxes or chips).
   - Selecting `general_user` disables all other role options.
   - Selecting any other role disables the `general_user` option.
   - UI displays clear validation messages when invalid combinations are attempted.

5. **Backward Compatibility**
   - Existing code that reads `user.role` (singular) is updated to read `user.roles` (array).
   - No breaking changes to authentication flow or session management.
   - Frontend components that check roles (e.g., `RoleGuard`, `useRole`) work correctly with role arrays.

## Tasks / Subtasks

- [ ] **Database: Design Multi-Role Schema** (AC: 3)
  - [ ] Decide between ARRAY column vs junction table approach.
    - **Recommendation**: PostgreSQL ARRAY for simplicity (roles are fixed, no additional metadata needed).
  - [ ] Create Alembic migration to:
    - Add new `roles` column as `ARRAY` (or create `user_roles` table).
    - Migrate existing `role` data to `roles` (e.g., `"admin"` → `["admin"]`).
    - Drop old `role` column (or deprecate).
  - [ ] Update `User` model in `backend/app/models/user.py`.

- [ ] **Database: Update Supabase Trigger** (AC: 3)
  - [ ] Modify `handle_new_user()` trigger to assign `roles = ["general_user"]` instead of `role = "general_user"`.
  - [ ] Update `auth.users` metadata to store roles as JSON array.

- [ ] **Backend: Refactor RBAC Logic** (AC: 2, 5)
  - [ ] Update `has_role()` in `backend/app/core/deps.py`:
    - Change from `current_user.role not in roles` to `not any(r in current_user.roles for r in roles)`.
  - [ ] Update `get_current_admin_user()` to check `"admin" in current_user.roles`.
  - [ ] Update all endpoints that reference `user.role` to use `user.roles`.

- [ ] **Backend: Role Validation Logic** (AC: 1)
  - [ ] Create validation function `validate_role_combination(roles: List[str]) -> bool`:
    - Return False if `"general_user" in roles and len(roles) > 1`.
    - Return True otherwise.
  - [ ] Add validation to user creation/update endpoints (`PUT /users/{id}/role` → `PUT /users/{id}/roles`).
  - [ ] Return 400 Bad Request with clear error message for invalid combinations.

- [ ] **Backend: Update User Service** (AC: 2, 5)
  - [ ] Update `UserService` methods to handle roles as arrays.
  - [ ] Ensure `create_user()` and `update_user_role()` work with role arrays.

- [ ] **Frontend: Update Role Components** (AC: 4, 5)
  - [ ] Update `useRole` hook to check `user.roles.includes(role)` instead of `user.role === role`.
  - [ ] Update `RoleGuard` component to work with role arrays.
  - [ ] Update all components that check `user.role` to use `user.roles`.

- [ ] **Frontend: Multi-Select Role UI** (AC: 4)
  - [ ] Replace single-select dropdown in Admin User Management with multi-select.
  - [ ] Use Shadcn/UI checkbox group or multi-select component.
  - [ ] Implement mutual exclusivity logic:
    - If `general_user` is selected, disable and clear other roles.
    - If any other role is selected, disable `general_user`.
  - [ ] Display validation error if user tries to save invalid combination.

- [ ] **Frontend: Display Multiple Roles** (AC: 4)
  - [ ] Update User List table to display multiple role badges per user.
  - [ ] Use Badge component with different colors for each role type.
  - [ ] Example: Admin + BPO user shows `[Admin Badge] [BPO Badge]`.

- [ ] **Testing** (AC: 1, 2, 3, 4, 5)
  - [ ] Unit test: `validate_role_combination()` accepts valid and rejects invalid combinations.
  - [ ] Unit test: `has_role()` correctly checks role arrays with OR logic.
  - [ ] Integration test: Assign multiple roles to a user via API, verify persisted correctly.
  - [ ] Integration test: Attempt to assign `["general_user", "admin"]`, verify 400 error.
  - [ ] Integration test: User with `["admin", "bpo"]` can access both admin and bpo endpoints.
  - [ ] E2E test: Admin assigns multiple roles via UI, verify badges display correctly.
  - [ ] Migration test: Run migration on test data, verify all single roles converted to arrays.

## Dev Notes

### Architecture Patterns

**Array vs Junction Table:**
- **Recommended: PostgreSQL ARRAY**
  - Simpler for fixed set of roles (admin, bpo, executive, general_user)
  - No additional join queries needed
  - Easy to query: `WHERE 'admin' = ANY(roles)`
  - Supabase/PostgreSQL native support

**Business Rule Enforcement:**
- Backend validation is mandatory (frontend is for UX only)
- Validation happens at:
  1. User creation (POST /users)
  2. Role update (PUT /users/{id}/roles)
  3. Supabase trigger (new registrations default to ["general_user"])

**RBAC Logic Change:**
- **Before:** User has exactly ONE role, check equality
- **After:** User has ONE OR MORE roles, check membership
- **Impact:** All `has_role()` checks must be updated

### Database Migration Strategy

**Alembic Migration Steps:**
1. Add new `roles` column as `TEXT[]` (PostgreSQL array), nullable=True
2. Populate `roles` from existing `role`: `UPDATE users SET roles = ARRAY[role]`
3. Make `roles` NOT NULL
4. Drop old `role` column
5. Update indexes if needed

**Rollback Plan:**
- Keep `role` column temporarily, mark as deprecated
- Populate it from `roles[0]` for backward compatibility
- Remove in next release after verification

### Source Tree Components

- `backend/app/models/user.py` (Modified - Change role to roles)
- `backend/app/core/deps.py` (Modified - Update has_role logic)
- `backend/app/api/v1/endpoints/users.py` (Modified - Multi-role CRUD)
- `backend/app/services/user_service.py` (Modified - Validation logic)
- `backend/alembic_migrations/versions/` (New migration file)
- `frontend/lib/role.tsx` (Modified - useRole and RoleGuard)
- `frontend/app/dashboard/admin/users/page.tsx` (Modified - Multi-select UI)
- Supabase `handle_new_user()` trigger (Modified via SQL Editor)

### Testing Standards

- **Unit Test Example:** `validate_role_combination(["general_user", "admin"])` → False
- **Integration Test Example:** PUT `/users/{id}/roles` with `["admin", "bpo"]` → 200 OK
- **E2E Test Example:** Admin selects multiple roles, saves, refreshes page → sees multiple badges

### Project Structure Notes

**Alignment:**
- Maintains existing RBAC architecture pattern
- Extends without breaking authentication flow
- Consistent with Supabase-based auth

**Conflicts:** None detected

### Learnings from Previous Stories

**From Story 2.2 (RBAC):**
- The `has_role()` dependency pattern is flexible and can be extended
- Tenant isolation logic is separate from role checks
- Frontend `RoleGuard` should mirror backend logic

**From Story 2.3 (Admin User Creation):**
- Role assignment UI is in `/dashboard/admin/users`
- Uses Shadcn/UI Select component for role selection
- Can be upgraded to multi-select without major refactor

### Business Rules

**Role Hierarchy (Not Enforced by System):**
- Admin: Full access to all features
- BPO: Control assessment + assigned processes
- Executive: Read-only dashboards
- General User: View approved data only

**Multi-Role Use Cases:**
- **Admin + BPO**: Small organization where admin also owns processes
- **BPO + Executive**: Process owner who needs executive dashboards
- **Admin + Executive**: Leadership who needs both admin and exec views

**Explicitly INVALID:**
- `["general_user", "admin"]` - General users can't have elevated privileges
- `["general_user", "bpo"]` - General users can't own processes

### References

- [Epic 2: User Identity & Access Management](docs/epics.md#epic-2-user-identity--access-management-iam) - Parent epic context for IAM
- [Epic 2 Tech Spec](docs/sprint-artifacts/tech-spec-epic-2.md) - Story 2.5 ACs 13-17 (multi-role support requirements)
- [System Architecture](docs/architecture.md) - Epic 2 IAM architecture, RBAC patterns, backend/app/core/security.py patterns
- [PRD: Permissions & Roles](docs/PRD.md#permissions--roles) - Business requirements for RBAC
- [Story 2.2: RBAC](docs/sprint-artifacts/2-2-implement-role-based-access-control-rbac.md) - Original single-role implementation

## Dev Agent Record

### Context Reference

- docs/sprint-artifacts/2-5-implement-multi-role-support.context.xml

### Agent Model Used

<!-- Will be filled during development -->

### Debug Log References

<!-- Will be filled during development -->

### Completion Notes List

<!-- Will be filled during development -->

### File List

<!-- Will be filled during development -->

## Change Log

**2025-12-13** - Story drafted by Bob (Scrum Master). Enhancement to support users with multiple organizational responsibilities.
