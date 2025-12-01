# Story 1.3: Implement API Endpoints for Core Data CRUD

Status: ready-for-dev

## Story

As an **Admin**,
I want **to be able to Create, Read, Update, and Delete the core compliance entities via the API**,
so that **the frontend has a secure and reliable way to manage the foundational data**.

## Acceptance Criteria

1.  **Given** the database schema from Story 1.2 and an authenticated Admin user,
2.  **When** a POST request is sent to `/api/v1/controls` with valid data,
3.  **Then** a new control is created in the database and a 201 status is returned.
4.  **And** GET (list and by ID), PUT, and DELETE endpoints are functional for `controls`, `risks`, `business_processes`, and `regulatory_frameworks`.
5.  **And** all API endpoints enforce tenant isolation based on the authenticated user's JWT token, failing with a 404 if a resource from another tenant is requested.

## Tasks / Subtasks

- [ ] **Implement API Endpoints for Controls** (AC: #2, #3, #4, #5)
  - [ ] Define Pydantic schemas for request/response bodies (e.g., `ControlCreate`, `ControlUpdate`).
  - [ ] Implement `POST /api/v1/controls` to create a new control.
  - [ ] Implement `GET /api/v1/controls` to list controls.
  - [ ] Implement `GET /api/v1/controls/{control_id}` to retrieve a single control.
  - [ ] Implement `PUT /api/v1/controls/{control_id}` to update a control.
  - [ ] Implement `DELETE /api/v1/controls/{control_id}` to delete a control.
  - [ ] Ensure `tenant_id` is automatically associated with created/updated resources based on authenticated user.
- [ ] **Implement API Endpoints for Risks, Business Processes, Regulatory Frameworks** (AC: #2, #3, #4, #5)
  - [ ] Define Pydantic schemas for request/response bodies for each entity.
  - [ ] Implement CRUD endpoints (`GET`, `POST`, `PUT`, `DELETE`) for each entity, similar to controls.
  - [ ] Ensure `tenant_id` is automatically associated with created/updated resources.
- [ ] **Implement Tenant Isolation with JWT** (AC: #5)
  - [ ] Configure FastAPI security to extract `tenant_id` from JWT.
  - [ ] Apply security dependencies to all CRUD endpoints to ensure only resources belonging to the authenticated user's tenant are accessible.
  - [ ] Handle cases where a user tries to access another tenant's resource (e.g., return 404 or 403).
- [ ] **Develop and execute integration tests for API endpoints** (AC: #1, #2, #3, #4, #5)
  - [ ] Write tests for `POST` endpoints to verify resource creation and correct tenant association.
  - [ ] Write tests for `GET` (list and by ID) endpoints, including positive and negative cases (e.g., accessing own vs. other tenant's resources).
  - [ ] Write tests for `PUT` endpoints to verify updates and tenant isolation.
  - [ ] Write tests for `DELETE` endpoints to verify resource deletion and tenant isolation.
  - [ ] Use `Pytest` for testing.

## Dev Notes


### Requirements Context Summary

This story focuses on implementing the RESTful API endpoints for CRUD operations on the core compliance entities (Business Processes, Risks, Controls, Regulatory Frameworks). The requirements are primarily derived from Story 1.3 in `epics.md` and the "APIs and Interfaces" section of `tech-spec-epic-1.md`.

-   **Purpose:** Provide secure and reliable backend services for managing foundational data.
-   **Entities:** Controls, Risks, Business Processes, Regulatory Frameworks.
-   **Operations:** Create, Read (list and by ID), Update, Delete.
-   **Technology:** FastAPI backend.
-   **Security:** All API endpoints must enforce tenant isolation based on the authenticated user's JWT token, failing with a 404 if a resource from another tenant is requested.
-   **Endpoints Structure:** Consistent `/api/v1/` prefix with plural, kebab-case resource names (e.g., `/api/v1/controls`).

### Learnings from Previous Story

**From Story 1.2 (Status: ready-for-dev)**

- **New Service Created**: Core database schema defined for `business_processes`, `risks`, `controls`, and `regulatory_frameworks`. This story will implement API interactions for these entities.
- **Architectural Decisions Reinforced**: Confirmation of FastAPI for backend and Supabase (PostgreSQL) for database.
- **Relevant Context File**: `docs/sprint-artifacts/1-2-define-migrate-core-database-schema.context.xml` provides detailed technical context for the database layer.
- **Relevant Code Paths**: Story 1.2 will create `backend/app/models/` for SQLAlchemy models and `backend/migrations/` for Alembic scripts. This story will interact with the models defined in `backend/app/models/`.

### Project Structure Notes

- Adhere strictly to the monorepo structure with distinct `frontend` and `backend` directories. API endpoints will reside in the `backend` project.

## Dev Agent Record

### Context Reference

- docs/sprint-artifacts/1-3-implement-api-endpoints-for-core-data-crud.context.xml

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

## Change Log

- **mandag 1. desember 2025:** Initial draft created by `create-story` workflow.

## Story

As an **Admin**,
I want **to be able to Create, Read, Update, and Delete the core compliance entities via the API**,
so that **the frontend has a secure and reliable way to manage the foundational data**.

## Acceptance Criteria

1.  **Given** the database schema from Story 1.2 and an authenticated Admin user,
2.  **When** a POST request is sent to `/api/v1/controls` with valid data,
3.  **Then** a new control is created in the database and a 201 status is returned.
4.  **And** GET (list and by ID), PUT, and DELETE endpoints are functional for `controls`, `risks`, `business_processes`, and `regulatory_frameworks`.
5.  **And** all API endpoints enforce tenant isolation based on the authenticated user's JWT token, failing with a 404 if a resource from another tenant is requested.

## Tasks / Subtasks

- [ ] **Implement API Endpoints for Controls** (AC: #2, #3, #4, #5)
  - [ ] Define Pydantic schemas for request/response bodies (e.g., `ControlCreate`, `ControlUpdate`).
  - [ ] Implement `POST /api/v1/controls` to create a new control.
  - [ ] Implement `GET /api/v1/controls` to list controls.
  - [ ] Implement `GET /api/v1/controls/{control_id}` to retrieve a single control.
  - [ ] Implement `PUT /api/v1/controls/{control_id}` to update a control.
  - [ ] Implement `DELETE /api/v1/controls/{control_id}` to delete a control.
  - [ ] Ensure `tenant_id` is automatically associated with created/updated resources based on authenticated user.
- [ ] **Implement API Endpoints for Risks, Business Processes, Regulatory Frameworks** (AC: #2, #3, #4, #5)
  - [ ] Define Pydantic schemas for request/response bodies for each entity.
  - [ ] Implement CRUD endpoints (`GET`, `POST`, `PUT`, `DELETE`) for each entity, similar to controls.
  - [ ] Ensure `tenant_id` is automatically associated with created/updated resources.
- [ ] **Implement Tenant Isolation with JWT** (AC: #5)
  - [ ] Configure FastAPI security to extract `tenant_id` from JWT.
  - [ ] Apply security dependencies to all CRUD endpoints to ensure only resources belonging to the authenticated user's tenant are accessible.
  - [ ] Handle cases where a user tries to access another tenant's resource (e.g., return 404 or 403).
- [ ] **Develop and execute integration tests for API endpoints** (AC: #1, #2, #3, #4, #5)
  - [ ] Write tests for `POST` endpoints to verify resource creation and correct tenant association.
  - [ ] Write tests for `GET` (list and by ID) endpoints, including positive and negative cases (e.g., accessing own vs. other tenant's resources).
  - [ ] Write tests for `PUT` endpoints to verify updates and tenant isolation.
  - [ ] Write tests for `DELETE` endpoints to verify resource deletion and tenant isolation.
  - [ ] Use `Pytest` for testing.

## Dev Notes


### Requirements Context Summary

This story focuses on implementing the RESTful API endpoints for CRUD operations on the core compliance entities (Business Processes, Risks, Controls, Regulatory Frameworks). The requirements are primarily derived from Story 1.3 in `epics.md` and the "APIs and Interfaces" section of `tech-spec-epic-1.md`.

-   **Purpose:** Provide secure and reliable backend services for managing foundational data.
-   **Entities:** Controls, Risks, Business Processes, Regulatory Frameworks.
-   **Operations:** Create, Read (list and by ID), Update, Delete.
-   **Technology:** FastAPI backend.
-   **Security:** All API endpoints must enforce tenant isolation based on the authenticated user's JWT token, failing with a 404 if a resource from another tenant is requested.
-   **Endpoints Structure:** Consistent `/api/v1/` prefix with plural, kebab-case resource names (e.g., `/api/v1/controls`).

### Learnings from Previous Story

**From Story 1.2 (Status: ready-for-dev)**

- **New Service Created**: Core database schema defined for `business_processes`, `risks`, `controls`, and `regulatory_frameworks`. This story will implement API interactions for these entities.
- **Architectural Decisions Reinforced**: Confirmation of FastAPI for backend and Supabase (PostgreSQL) for database.
- **Relevant Context File**: `docs/sprint-artifacts/1-2-define-migrate-core-database-schema.context.xml` provides detailed technical context for the database layer.
- **Relevant Code Paths**: Story 1.2 will create `backend/app/models/` for SQLAlchemy models and `backend/migrations/` for Alembic scripts. This story will interact with the models defined in `backend/app/models/`.

### Project Structure Notes

- Adhere strictly to the monorepo structure with distinct `frontend` and `backend` directories. API endpoints will reside in the `backend` project.

## Dev Agent Record

### References

- [Source: `docs/epics.md#Story 1.3: Implement API Endpoints for Core Data CRUD`]
- [Source: `docs/sprint-artifacts/tech-spec-epic-1.md#APIs and Interfaces`]
- [Source: `docs/architecture.md#7. Implementation Patterns (Consistency Rules)`]
- [Source: `docs/architecture.md#4.1. Data Persistence`]

## Dev Agent Record

### Context Reference

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

## Change Log

- **mandag 1. desember 2025:** Initial draft created by `create-story` workflow.

