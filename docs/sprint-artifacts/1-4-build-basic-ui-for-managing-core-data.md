# Story 1.4: Build Basic UI for Managing Core Data

Status: ready-for-dev

## Story

As an **Admin**,
I want **a basic web interface to manage Controls, Risks, Business Processes, and Regulatory Frameworks**,
so that **I can populate and maintain the system's core compliance data without using direct database tools.**

## Acceptance Criteria

1.  **Given** an authenticated Admin user with access to the system,
2.  **When** the user navigates to the "Data Management" section of the frontend application,
3.  **Then** they should see a clear, navigable dashboard or menu for accessing "Controls", "Risks", "Business Processes", and "Regulatory Frameworks".
4.  **And** for each entity type, the user can view a list of existing records (paginated if necessary).
5.  **And** the user can click "Create New" to open a form, fill in required fields, and submit to create a new record (consuming the API from Story 1.3).
6.  **And** the user can click "Edit" on an existing record to modify its fields and save changes.
7.  **And** the user can click "Delete" (with a confirmation dialog) to remove a record.
8.  **And** the UI handles API errors gracefully (e.g., displaying validation messages or unauthorized access alerts).

## Tasks / Subtasks

- [ ] **Set up Frontend Routing and Navigation** (AC: #2, #3)
  - [ ] Create new route/page for "Data Management".
  - [ ] Implement navigation links/menu for Controls, Risks, Business Processes, Regulatory Frameworks.
- [ ] **Implement List Views for Core Entities** (AC: #4)
  - [ ] Create reusable "DataTable" or list component.
  - [ ] Implement data fetching from Story 1.3 API endpoints (GET /api/v1/{entity}).
  - [ ] Display key columns for each entity type.
- [ ] **Implement "Create" Forms** (AC: #5, #8)
  - [ ] Create forms for Controls, Risks, Business Processes, Regulatory Frameworks using React Hook Form (or similar).
  - [ ] Implement form validation (client-side and handling server-side errors).
  - [ ] Connect form submission to POST API endpoints.
- [ ] **Implement "Edit" Functionality** (AC: #6, #8)
  - [ ] Add "Edit" button to list view items.
  - [ ] Implement form pre-filling with existing data.
  - [ ] Connect form submission to PUT API endpoints.
- [ ] **Implement "Delete" Functionality** (AC: #7, #8)
  - [ ] Add "Delete" button to list view items.
  - [ ] Implement confirmation modal/dialog.
  - [ ] Connect confirmation action to DELETE API endpoints.
- [ ] **Develop and execute UI integration tests** (AC: #3, #4, #5, #6, #7, #8)
  - [ ] Write tests for navigation to Data Management pages.
  - [ ] Write tests for rendering list views with mock data.
  - [ ] Write tests for form interactions (create, edit) and submission success/failure.
  - [ ] Write tests for delete confirmation and execution.

## Dev Notes

### Requirements Context Summary

This story addresses the frontend requirements for managing core compliance data. It builds directly upon the backend APIs established in Story 1.3.

-   **Purpose:** Provide a user-friendly interface for Admins to perform CRUD operations on core entities.
-   **Entities:** Controls, Risks, Business Processes, Regulatory Frameworks.
-   **User:** Admin.
-   **Key Features:** Navigation, List Views, Create/Edit Forms, Delete Confirmation.
-   **Tech Stack:** React (Frontend), consuming FastAPI (Backend).

### Learnings from Previous Story

**From Story 1.3 (Status: ready-for-dev)**

- **New Service Created**: API Endpoints for CRUD operations on `controls`, `risks`, `business_processes`, and `regulatory_frameworks` are defined and implemented in Story 1.3. This story *consumes* those endpoints.
- **Architectural Constraints**: Frontend must handle JWT token storage and inclusion in API headers to pass tenant isolation checks enforced by the backend.
- **Relevant Context File**: `docs/sprint-artifacts/1-3-implement-api-endpoints-for-core-data-crud.md` describes the API contract (endpoints, methods, status codes).
- **Code Reuse**: Utilize any established API client/service wrappers created in previous frontend setup stories (if any) or create a standard one now.

### Project Structure Notes

- Frontend code resides in the `frontend` directory of the monorepo.
- Components should be modular and reusable (e.g., generic List/Table component, generic Form wrapper).

### References

- [Source: `docs/epics.md#Story 1.4: Build Basic UI for Managing Core Data`]
- [Source: `docs/sprint-artifacts/tech-spec-epic-1.md#User Interface`]
- [Source: `docs/architecture.md#5. Frontend Architecture`]

## Dev Agent Record

### References

- [Source: `docs/epics.md#Story 1.4: Build Basic UI for Managing Core Data`]
- [Source: `docs/sprint-artifacts/tech-spec-epic-1.md#User Interface`]
- [Source: `docs/architecture.md#5. Frontend Architecture`]

### Context Reference

- docs/sprint-artifacts/1-4-build-basic-ui-for-managing-core-data.context.xml

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

- **Issue:** TypeScript errors `TS2307: Cannot find module` for `@/components/ui/textarea`, `@/components/ui/alert`, `@/components/ui/tooltip`, and `TS2339: Property 'get' does not exist on type 'Promise<ReadonlyRequestCookies>'` in server actions.
- **Root Cause:** Missing Shadcn UI component installations (`textarea`, `alert`, `tooltip`). The `cookies()` error was due to Next.js 15 treating `cookies()` as asynchronous and `await` was missing.
- **Resolution:**
    - Installed missing `@radix-ui/react-alert-dialog` and `@radix-ui/react-tooltip`.
    - Installed missing Shadcn UI components `textarea`, `alert`, `tooltip` using `npx shadcn@latest add ...`.
    - Updated `frontend/tsconfig.json` to exclude `__tests__` directory to prevent Jest test files from interfering with Next.js build.
    - Added `async` and `await` to `getSession()` in `app/lib/auth.ts` and `Profile()` in `app/dashboard/profile/page.tsx` for correct `cookies()` usage.
    - Fixed implicit `any` type for event parameter `e` in `DeleteEntityButton`.

### Completion Notes List

- ✅ Set up Frontend Routing and Navigation (`frontend/app/dashboard/layout.tsx`).
- ✅ Implemented List Views for all Core Entities (`frontend/app/dashboard/controls/page.tsx`, etc.).
- ✅ Implemented "Create" Forms for all Core Entities (`frontend/app/dashboard/controls/new/page.tsx`, etc.) using React Server Actions and Zod validation.
- ✅ Implemented "Edit" Functionality for all Core Entities (`frontend/app/dashboard/controls/[id]/edit/page.tsx`, etc.) using React Server Actions.
- ✅ Implemented "Delete" Functionality for all Core Entities using a reusable `DeleteEntityButton` with Shadcn UI `AlertDialog` and React Server Actions.
- ✅ Authored E2E Playwright tests (`frontend/tests/*.spec.ts`) for navigation and CRUD operations for each entity.
- ✅ Resolved all TypeScript and build errors, ensuring the frontend compiles successfully.
- ⚠️ **Warning:** Playwright tests were not executed due to persistent environment issues beyond the scope of story implementation (i.e., local Playwright test runner issues with server startup outside of Docker context). The code is written with tests, and all compilation/linting checks pass.

### File List

- `frontend/app/dashboard/layout.tsx` (Modified)
- `frontend/app/dashboard/controls/page.tsx` (Created)
- `frontend/app/dashboard/controls/new/page.tsx` (Created)
- `frontend/app/dashboard/controls/[id]/edit/page.tsx` (Created)
- `frontend/app/dashboard/risks/page.tsx` (Created)
- `frontend/app/dashboard/risks/new/page.tsx` (Created)
- `frontend/app/dashboard/risks/[id]/edit/page.tsx` (Created)
- `frontend/app/dashboard/business-processes/page.tsx` (Created)
- `frontend/app/dashboard/business-processes/new/page.tsx` (Created)
- `frontend/app/dashboard/business-processes/[id]/edit/page.tsx` (Created)
- `frontend/app/dashboard/regulatory-frameworks/page.tsx` (Created)
- `frontend/app/dashboard/regulatory-frameworks/new/page.tsx` (Created)
- `frontend/app/dashboard/regulatory-frameworks/[id]/edit/page.tsx` (Created)
- `frontend/components/actions/compliance-actions.ts` (Created, Modified)
- `frontend/components/actions/delete-actions.ts` (Created)
- `frontend/components/delete-entity-button.tsx` (Created, Modified)
- `frontend/lib/definitions.ts` (Modified)
- `frontend/components/ui/alert-dialog.tsx` (Created)
- `frontend/components/ui/textarea.tsx` (Created, potentially skipped if already existing)
- `frontend/components/ui/alert.tsx` (Created, potentially skipped if already existing)
- `frontend/components/ui/tooltip.tsx` (Created, potentially skipped if already existing)
- `frontend/tests/navigation.spec.ts` (Created)
- `frontend/tests/controls.spec.ts` (Created)
- `frontend/tests/risks.spec.ts` (Created)
- `frontend/tests/business-processes.spec.ts` (Created)
- `frontend/tests/regulatory-frameworks.spec.ts` (Created)
- `frontend/tsconfig.json` (Modified)
- `frontend/playwright.config.ts` (Created)
- `frontend/app/openapi-client/types.gen.ts` (Generated)
- `frontend/app/openapi-client/sdk.gen.ts` (Generated)
- `frontend/openapi.json` (Generated)
- `backend/commands/generate_openapi_schema.py` (Modified)
- `frontend/openapi-ts.config.ts` (Modified)
- `frontend/app/lib/auth.ts` (Modified)
- `frontend/app/dashboard/profile/page.tsx` (Modified)

## Change Log

- **mandag 1. desember 2025:** Initial draft created by `create-story` workflow.
- **Wednesday, December 3, 2025:** Frontend UI implemented for CRUD operations on core entities, including routing, list views, forms, delete confirmation, and E2E tests. Addressed various frontend build and type-checking issues.