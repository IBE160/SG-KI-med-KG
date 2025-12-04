# Story 2.1: Implement User Registration & Login (Email/Password)

Status: drafted

## Story

As a **new user**,
I want **to securely register for an account and log in using email and password**,
so that **I can access the application's features as an authenticated user**.

## Acceptance Criteria

1. **Given** I am on the registration page,
2. **When** I provide a valid email and password (meeting complexity requirements),
3. **Then** my account is created, and I receive an email verification link.
4. **And** after verifying my email, I can log in successfully.
5. **And** upon login, I am assigned the "General User" role by default within a tenant.

## Tasks / Subtasks

- [ ] **Configure Supabase Auth for Email/Password** (AC: #2, #3, #4)
  - [ ] Verify Supabase project settings enable email/password authentication
  - [ ] Configure email templates for verification and password reset
  - [ ] Set password complexity requirements (min 8 chars, complexity rules)
  - [ ] Configure SendGrid integration for transactional emails

- [ ] **Implement Backend Authentication Integration** (AC: #2, #5)
  - [ ] Review and update `backend/app/core/security.py` for Supabase JWT validation
  - [ ] Implement middleware to extract and validate JWT tokens from Authorization header
  - [ ] Create user profile model with `tenant_id` and `role` fields
  - [ ] Implement default role assignment logic (General User) on registration

- [ ] **Build Registration UI** (AC: #1, #2, #3)
  - [ ] Create registration page at `frontend/app/(auth)/register/page.tsx`
  - [ ] Build registration form with email and password fields using React Hook Form
  - [ ] Implement client-side password validation (complexity requirements)
  - [ ] Add Zod schema validation for form inputs
  - [ ] Integrate Supabase client `signUp` method
  - [ ] Display email verification prompt after successful registration
  - [ ] Handle and display registration errors (duplicate email, weak password, etc.)

- [ ] **Build Login UI** (AC: #4)
  - [ ] Create login page at `frontend/app/(auth)/login/page.tsx`
  - [ ] Build login form with email and password fields
  - [ ] Integrate Supabase client `signInWithPassword` method
  - [ ] Store JWT token in HTTP-only cookie or secure session storage
  - [ ] Redirect authenticated users to dashboard
  - [ ] Handle and display login errors (invalid credentials, unverified email, etc.)

- [ ] **Implement Password Reset Flow** (Out of scope for MVP, noted for future)
  - [ ] Create "Forgot Password" link on login page
  - [ ] Implement password reset request flow
  - [ ] Create password reset confirmation page

- [ ] **Write Integration Tests** (AC: #2, #3, #4, #5)
  - [ ] Write backend test for user registration and role assignment
  - [ ] Write backend test for JWT validation middleware
  - [ ] Write Playwright E2E test for registration flow (form submission, email sent)
  - [ ] Write Playwright E2E test for email verification flow (requires test email service)
  - [ ] Write Playwright E2E test for login flow (successful and failed attempts)
  - [ ] Write Playwright E2E test for authenticated route protection

## Dev Notes

### Requirements Context Summary

This story implements the foundational authentication system for the ibe160 platform, enabling users to securely register and access the application.

- **Primary Goal**: Enable user registration with email/password and secure login
- **Authentication Provider**: Supabase Auth
- **Email Service**: SendGrid (configured in Story 1.1)
- **Default Role**: General User (within tenant)
- **Security Requirements**: Password complexity, email verification, TLS 1.2+, OWASP compliance

### Learnings from Previous Story

**From Story 1.4 (Status: done)**

- **New Frontend Patterns**: Server Actions pattern established in `frontend/components/actions/compliance-actions.ts` - use similar pattern for auth actions if needed
- **Component Library**: Shadcn UI components installed and configured (`AlertDialog`, `Alert`, `textarea`, `tooltip`) - reuse for form validation feedback
- **Environment Configuration**: `NEXT_PUBLIC_API_URL` pattern established in `frontend/.env.local` - ensure Supabase keys follow similar pattern (`NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`)
- **Error Handling**: Established pattern of using `try/catch` in server actions with `Alert` component for user feedback
- **Testing Setup**: Playwright E2E framework initialized - extend for auth flow testing
- **Development Environment**: SQLite used for local backend; CORS configured for `localhost:3001` fallback

[Source: docs/sprint-artifacts/1-4-build-basic-ui-for-managing-core-data.md#Dev-Agent-Record]

### Project Structure Notes

- **Backend Auth**: `backend/app/core/security.py` - JWT validation, role management
- **Frontend Auth Pages**: `frontend/app/(auth)/` - login, register routes (Next.js route groups)
- **Supabase Client**: `frontend/lib/supabase.ts` (or similar) - client instance for auth methods
- **Middleware**: `frontend/middleware.ts` - Already protects dashboard routes, may need auth state updates

### References

- [Source: docs/PRD.md#FR-1: Role-Based Access Control]
- [Source: docs/epics.md#Story 2.1: Implement User Registration & Login]
- [Source: docs/architecture.md#4.2 Deployment Targets]
- [Source: docs/architecture.md#4.7 Email Service]

### Technical Implementation Notes

**Supabase Auth Configuration:**
- The `vintasoftware/nextjs-fastapi-template` includes `fastapi-users` for authentication, but this project uses Supabase Auth
- Need to reconcile or replace existing auth setup with Supabase Auth
- Supabase provides Row-Level Security (RLS) which will be leveraged for tenant isolation

**JWT Token Flow:**
1. User registers → Supabase creates account → Email verification sent
2. User verifies email → Account activated
3. User logs in → Supabase returns JWT in response
4. Frontend stores JWT securely (HTTP-only cookie preferred)
5. All API requests include JWT in Authorization header
6. Backend validates JWT signature using Supabase public key
7. Backend extracts user claims (user_id, tenant_id, role) from JWT

**Role Assignment Strategy:**
- Default role: "General User"
- Role stored in custom claims or user metadata in Supabase
- Admin can change roles via future user management UI (Story 2.2)

**Security Considerations:**
- Password requirements: minimum 8 characters, mix of upper/lower/numbers/symbols
- Rate limiting on auth endpoints (consider future implementation)
- HTTPS enforced in production (TLS 1.2+)
- JWT expiration and refresh token strategy
- Protection against common attacks: SQL injection, XSS, CSRF (use OWASP guidelines)

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

Claude 3.5 Sonnet (claude-sonnet-4-5-20250929)

### Debug Log References

<!-- Will be populated during implementation -->

### Completion Notes List

<!-- Will be populated during implementation -->

### File List

<!-- Will be populated during implementation -->

## Change Log

- **Wednesday, December 4, 2025:** Initial draft created by `create-story` workflow (SM Agent: Bob)
