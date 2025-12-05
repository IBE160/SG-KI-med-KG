# Story 2.2: Implement Role-Based Access Control (RBAC)

Status: ready-for-dev

## Story

As an **Admin**,
I want **to manage user roles (Admin, BPO, Executive, General User) within my tenant**,
so that **I can control access to features and data according to defined permissions**.

## Acceptance Criteria

1. **Given** I am logged in as an Admin,
2. **When** I access the user management interface,
3. **Then** I see a list of users in my tenant with their current roles.
4. **And** I can change a user's role to Admin, BPO, Executive, or General User.
5. **And** the system enforces permissions: General Users cannot access Admin features or endpoints.
6. **And** user roles are persisted in the database and enforced effectively (e.g., via JWT claims or DB lookup).

## Tasks / Subtasks

- [ ] **Implement Backend Role Management** (AC: #4, #6)
  - [ ] Add `PUT /api/v1/users/{user_id}/role` endpoint (Admin only)
  - [ ] Implement service logic to update user role in `users` table
  - [ ] (Optional) Sync role update to Supabase Auth `user_metadata` for easier frontend access

- [ ] **Implement RBAC Middleware / Dependencies** (AC: #5)
  - [ ] Create `get_current_active_user` dependency (already likely exists)
  - [ ] Create `get_current_admin_user` dependency (checks role="admin")
  - [ ] Create generic `has_role(roles: List[str])` dependency factory for route protection
  - [ ] Protect user management endpoints with `has_role(["admin"])`

- [ ] **Build Admin User Management UI** (AC: #2, #3, #4)
  - [ ] Create `/admin/users` page (protected route)
  - [ ] Fetch and display list of users (name, email, role, status)
  - [ ] Implement "Edit Role" functionality (Modal or inline dropdown)
  - [ ] Connect "Save" action to backend `PUT` endpoint
  - [ ] Handle errors and success notifications (Toast/Alert)

- [ ] **Enforce Frontend Permissions** (AC: #5)
  - [ ] Create `RoleGuard` component or hook (e.g., `useRole`) to conditionally render UI
  - [ ] Hide "Admin" navigation links for non-admin users
  - [ ] Redirect unauthorized access to `/admin/*` routes to dashboard or 403 page

- [ ] **Write Tests** (AC: #1-6)
  - [ ] Backend: Unit tests for `has_role` dependency
  - [ ] Backend: Integration test for role update endpoint (Admin vs Non-Admin access)
  - [ ] Frontend: Unit test for `RoleGuard` (renders/hides correctly)
  - [ ] E2E: Playwright test for Admin changing a user's role
  - [ ] E2E: Playwright test verifying General User cannot access Admin page

## Dev Notes

### Requirements Context Summary

This story builds upon the authentication system from Story 2.1 to implement authorization. It distinguishes between users by assigning roles and enforcing access boundaries.

- **Roles**: Admin, BPO, Executive, General User.
- **Tenant Isolation**: Admins can only see/manage users in their tenant.
- **Enforcement**: Both API (security) and UI (usability).

### Learnings from Previous Story

**From Story 2.1 (Status: ready-for-dev)**

- **Implementation Pending**: Story 2.1 is ready but code has not been written yet.
- **Design Alignment**: Ensure the `users` table schema defined in 2.1 (or Epic 2 Tech Spec) supports the `role` column as expected.
- **Authentication**: Usage of Supabase Auth established. This story extends it by adding the authorization layer.

[Source: docs/sprint-artifacts/2-1-implement-user-registration-login-email-password.md]

### Project Structure Notes

- **Backend**: `backend/app/api/v1/endpoints/users.py` for user management endpoints.
- **Security**: `backend/app/core/security.py` or `deps.py` for RBAC dependencies.
- **Frontend**: `frontend/app/(dashboard)/admin/users/page.tsx` for the UI.
- **Components**: Reuse Shadcn UI Table and Dialog/Select for the management interface.

### References

- [Source: docs/tech-spec-epic-2.md#Detailed Design] - Defines `users` table and endpoints.
- [Source: docs/epics.md#Story 2.2: Implement Role-Based Access Control]
- [Source: docs/PRD.md#FR-1: Role-Based Access Control]

### Technical Implementation Notes

**Role Storage vs. Claims:**
- The Tech Spec defines a `role` column in the `users` table.
- **Recommendation**: Update the local `users` table `role` column.
- **Optimization**: Also update Supabase `raw_user_meta_data` with the role. This allows the JWT from Supabase to contain the role, making `get_current_user` faster (no DB lookup needed if trusted) or at least available to the frontend immediately on login.
- **Validation**: Backend *must* validate the role against the database or a signed JWT claim to ensure security.

**Frontend RBAC:**
- Use a Context or Hook (`useAuth`) that provides the current user's role.
- Wrap Admin routes in a layout that checks the role and redirects if insufficient.

## Dev Agent Record

### Context Reference

- docs/sprint-artifacts/2-2-implement-role-based-access-control-rbac.context.xml

### Agent Model Used

<!-- Will be populated during implementation -->

### Debug Log References

<!-- Will be populated during implementation -->

### Completion Notes List

<!-- Will be populated during implementation -->

### File List

<!-- Will be populated during implementation -->

## Change Log

- **Friday, December 5, 2025:** Initial draft created by `create-story` workflow (SM Agent: Bob)