# Epic Technical Specification: User Identity & Access Management (IAM)

Date: 2025-12-01
Author: BIP
Epic ID: 2
Status: Draft

---

## Overview

This document provides the technical specification for Epic 2: User Identity & Access Management (IAM). The goal of this epic is to enable secure user access and enforce role-based permissions, ensuring that users can only see and do what their roles permit. This covers user registration, login, and the ability for Admins to manage roles. This epic directly addresses FR-1 (Role-Based Access Control).

## Objectives and Scope

**In Scope:**
*   Implementing user registration with email and password via Supabase Auth.
*   Email verification for new accounts.
*   Secure user login and session management (JWT).
*   Default role assignment ("General User") upon registration.
*   An admin interface for managing user roles (Admin, BPO, Executive, General User).
*   API middleware/decorators to enforce role-based access on protected endpoints.
*   Dynamically rendering UI elements based on the authenticated user's role.

**Out of Scope:**
*   Social logins (e.g., Google, GitHub).
*   Multi-factor authentication (MFA).
*   "Remember me" functionality.
*   More granular, position-based permissions (slated for Growth phase).

## System Architecture Alignment

This epic builds upon the foundation of Epic 1 and leverages several key architectural decisions. User management will be handled by **Supabase Auth**, as planned. The frontend registration and login forms will be built in the **Next.js** application, while the backend **FastAPI** application will validate JWTs passed in the `Authorization` header to protect its endpoints. Role-based logic will be implemented in both the frontend (to show/hide UI elements) and backend (to authorize API requests), adhering to the patterns established in the architecture document. Transactional emails for verification will be sent via **SendGrid**.

## Detailed Design

### Services and Modules

| Service/Module | Responsibilities | Inputs | Outputs | Owner |
| :--- | :--- | :--- | :--- | :--- |
| **`backend.app.api.v1.auth`** | FastAPI endpoints for user registration, login, role management. | User credentials, Role IDs | JWT, User objects | `dev` |
| **`backend.app.core.security`** | Middleware for JWT validation and role-based authorization. | JWT | Boolean (authorized/not) | `dev` |
| **`frontend.app/(auth)`** | Next.js pages for registration and login. | User input | Rendered forms | `dev` |
| **`frontend.app/(dashboard)/admin/users`** | Next.js page for Admin to manage user roles. | User ID, Role ID | Updated user object | `dev` |

### Data Models and Contracts

**User Model (`users` table):**
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  is_superuser BOOLEAN DEFAULT FALSE,
  is_verified BOOLEAN DEFAULT FALSE,
  role VARCHAR(50) NOT NULL DEFAULT 'general_user', -- admin, bpo, executive, general_user
  tenant_id UUID NOT NULL
);
```

### APIs and Interfaces

**Authentication Endpoints (`/api/v1/auth`):**
*   `POST /register`: Register new user.
*   `POST /login`: Authenticate user, return JWT.
*   `POST /verify-email`: Verify user email.

**User Management Endpoints (protected, `/api/v1/users`):**
*   `PUT /{user_id}/role`: Admin only, update user role.

### Workflows and Sequencing

1.  **Frontend Auth UI:** Build registration and login pages.
2.  **Backend Auth Endpoints:** Implement FastAPI endpoints using `fastapi-users`.
3.  **Role Management UI:** Build Admin page for changing roles.
4.  **Backend RBAC:** Implement middleware for role-based authorization.

## Non-Functional Requirements

### Performance

*   User registration and login must complete within 1 second.
*   Role update operations must complete within 500ms.

### Security

*   All user data must be protected by robust password hashing.
*   JWT tokens must be validated on every protected API request.
*   Role-based access must be enforced on both frontend and backend.
*   Email verification must be securely implemented.

### Reliability/Availability

*   Supabase Auth provides high availability for user management.
*   SendGrid integration must handle email sending failures gracefully.

### Observability

*   Authentication events (login, registration, failed attempts) must be logged.
*   Role changes by administrators must be logged.

## Dependencies and Integrations

*   **`Supabase Auth`**: For user registration, login, session management, and JWT generation.
*   **`fastapi-users`**: FastAPI integration for user management.
*   **`SendGrid`**: For sending email verification links.
*   **`Next.js`**: Frontend framework for UI.

## Acceptance Criteria (Authoritative)

**Story 2.1: User Registration & Login**
1.  A new user can successfully register, verify their email, and log in.
2.  Upon successful login, the user is assigned the "General User" role by default.

**Story 2.2: Role-Based Access Control (RBAC)**
3.  An Admin user can access a user management interface.
4.  An Admin can change a user's role to Admin, BPO, Executive, or General User.
5.  Users can only access features and data appropriate for their assigned role (e.g., General User cannot access Admin functions, BPO cannot access Executive dashboards unless explicitly permitted).
6.  Frontend UI dynamically renders elements based on the logged-in user's role.

**Story 2.3: Admin User Creation & Role Assignment**
7.  Admin can create new users and assign them roles directly from the admin interface.
8.  Created users appear in the user list with their assigned roles.

**Story 2.4: Fix Default Tenant Assignment** _(Post-MVP fix)_
9.  All new user registrations are assigned to the default tenant (095b5d35-992e-482b-ac1b-d9ec10ac1425).
10. No new tenants are created during user registration.
11. All existing users are consolidated into the default tenant.
12. Users within the default tenant can collaborate and see shared compliance data.

## Traceability Mapping

| AC | Spec Section(s) | Component(s)/API(s) | Test Idea |
| :- | :--- | :--- | :--- |
| 1-2| Story 2.1 | `frontend/(auth)`, `backend/api/v1/auth`, `Supabase Auth` | E2E registration/login tests |
| 3-6| Story 2.2 | `frontend/(dashboard)/admin/users`, `backend/api/v1/users`, `backend/core/security` | E2E role management tests, middleware tests |
| 7-8| Story 2.3 | `frontend/(dashboard)/admin/users`, `backend/api/v1/users` | Admin user creation flow tests |
| 9-12| Story 2.4 | Supabase `handle_new_user()` trigger, `backend/scripts/consolidate_tenant.py` | Database query verification, multi-user collaboration test |

## Risks, Assumptions, Open Questions

*   **Risk:** Overly complex RBAC implementation. **Mitigation:** Start with a simple role hierarchy and expand as needed.
*   **Risk:** Tenant isolation prevents user collaboration. **Resolution:** Story 2.4 fixes this by consolidating to a single default tenant for MVP.
*   **Assumption:** Supabase Auth is sufficient for all MVP authentication needs.
*   **Assumption:** Single-tenant approach is acceptable for MVP/school project. Multi-tenant invitation system will be implemented post-MVP if commercialized.
*   **Question:** What are the exact screens/UI for the Admin user management? (Defer to UX Design)

## Test Strategy Summary

*   **Unit Tests:** Backend unit tests for security middleware and user service functions.
*   **Integration Tests:** API integration tests for registration, login, and role update endpoints.
*   **E2E Tests:** Playwright tests for user registration, login flows, and Admin role management UI.
*   **Security Tests:** Manual checks for unauthorized access based on roles.

## Post-Review Follow-ups

*   **Code Changes Required:**
    *   [x] [High] Verify database migrations run successfully once DB environment is fixed (AC #5) - Ref: Story 2.1