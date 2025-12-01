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

### Context Reference

- docs/sprint-artifacts/1-4-build-basic-ui-for-managing-core-data.context.xml

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

## Change Log

- **mandag 1. desember 2025:** Initial draft created by `create-story` workflow.