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

- [x] **Implement API Endpoints for Controls** (AC: #2, #3, #4, #5)
  - [x] Define Pydantic schemas for request/response bodies (e.g., `ControlCreate`, `ControlUpdate`).
  - [x] Implement `POST /api/v1/controls` to create a new control.
  - [x] Implement `GET /api/v1/controls` to list controls.
  - [x] Implement `GET /api/v1/controls/{control_id}` to retrieve a single control.
  - [x] Implement `PUT /api/v1/controls/{control_id}` to update a control.
  - [x] Implement `DELETE /api/v1/controls/{control_id}` to delete a control.
  - [x] Ensure `tenant_id` is automatically associated with created/updated resources based on authenticated user.
- [x] **Implement API Endpoints for Risks, Business Processes, Regulatory Frameworks** (AC: #2, #3, #4, #5)
  - [x] Define Pydantic schemas for request/response bodies for each entity.
  - [x] Implement CRUD endpoints (`GET`, `POST`, `PUT`, `DELETE`) for each entity, similar to controls.
  - [x] Ensure `tenant_id` is automatically associated with created/updated resources.
- [x] **Implement Tenant Isolation with JWT** (AC: #5)
  - [x] Configure FastAPI security to extract `tenant_id` from JWT.
  - [x] Apply security dependencies to all CRUD endpoints to ensure only resources belonging to the authenticated user's tenant are accessible.
  - [x] Handle cases where a user tries to access another tenant's resource (e.g., return 404 or 403).
- [x] **Develop and execute integration tests for API endpoints** (AC: #1, #2, #3, #4, #5)
  - [x] Write tests for `POST` endpoints to verify resource creation and correct tenant association.
  - [x] Write tests for `GET` (list and by ID) endpoints, including positive and negative cases (e.g., accessing own vs. other tenant's resources).
  - [x] Write tests for `PUT` endpoints to verify updates and tenant isolation.
  - [x] Write tests for `DELETE` endpoints to verify resource deletion and tenant isolation.
  - [x] Use `Pytest` for testing.

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

### Context Reference

- docs/sprint-artifacts/1-3-implement-api-endpoints-for-core-data-crud.context.xml

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

- **Issue:** Tests failed locally due to `socket.gaierror: [Errno 11001] getaddrinfo failed`.
- **Root Cause:** Tests are configured to connect to `db_test` host (from `docker-compose.yml`), but tests were run locally where this hostname is not resolvable. Attempting to run via `docker-compose run` failed because the Docker daemon is not running.
- **Resolution:** User started Docker. Tests successfully executed via `docker-compose run --rm backend uv run pytest` with 46/46 tests passing (including 18 new compliance tests).

### Completion Notes List



- ✅ Implemented Pydantic schemas for Controls, Risks, Business Processes, and Regulatory Frameworks in `backend/app/schemas.py`.

- ✅ Implemented CRUD API endpoints for all core entities in `backend/app/routes/compliance.py`.

- ✅ Configured tenant isolation using `user.id` as `tenant_id` for the MVP (as per current User model limitations).

- ✅ Added integration tests in `backend/tests/test_compliance.py` covering Create, Read, Update, and Delete operations.

- ✅ Updated `backend/tests/conftest.py` to fix fixture naming (`client` -> `test_client`) and add missing `superuser_token_headers` fixture.

- ✅ **Verification:** All tests passed successfully (46/46), confirming correct implementation of API endpoints and schemas.



### File List



- `backend/app/schemas.py` (Modified)

- `backend/app/routes/compliance.py` (Created)

- `backend/app/main.py` (Modified)

- `backend/tests/conftest.py` (Modified)

- `backend/tests/test_compliance.py` (Created)



## Change Log



- **mandag 1. desember 2025:** Initial draft created by `create-story` workflow.

- **Wednesday, December 3, 2025:** Implemented API endpoints, schemas, and tests. Updated test configuration.

- **Wednesday, December 3, 2025:** Senior Developer Review notes appended.



## Senior Developer Review (AI)



**Reviewer:** BIP

**Date:** Wednesday, December 3, 2025

**Outcome:** Approve



### Summary

The implementation correctly establishes the core data management APIs for controls, risks, business processes, and regulatory frameworks. The code follows the project's architectural patterns, using FastAPI, Pydantic, and SQLAlchemy. Tenant isolation is correctly implemented at the API level using the authenticated user's ID, which is an acceptable MVP strategy. Comprehensive integration tests were added and verified to pass.



### Key Findings

- **High Severity:** None.

- **Medium Severity:** None.

- **Low Severity:**

    - **Tenant ID Handling:** The current implementation relies on `user.id` as `tenant_id`. While valid for MVP, this will need refactoring when true multi-user tenant support is added (Action Item created).



### Acceptance Criteria Coverage



| AC# | Description | Status | Evidence |

| :--- | :--- | :--- | :--- |

| 1 | **Given** database schema & admin user | IMPLEMENTED | `backend/tests/conftest.py` (fixtures) |

| 2 | **When** POST /api/v1/controls | IMPLEMENTED | `backend/app/routes/compliance.py:23` |

| 3 | **Then** new control created & 201 status | IMPLEMENTED | `backend/app/routes/compliance.py:23` (status_code=201) |

| 4 | **And** GET/PUT/DELETE functional for all entities | IMPLEMENTED | `backend/app/routes/compliance.py` (lines 43, 56, 71, 89 etc.) |

| 5 | **And** API endpoints enforce tenant isolation | IMPLEMENTED | `backend/app/routes/compliance.py` (e.g., line 51: `filter(Control.tenant_id == tenant_id)`) |



**Summary:** 5 of 5 acceptance criteria fully implemented.



### Task Completion Validation



| Task | Marked As | Verified As | Evidence |

| :--- | :--- | :--- | :--- |

| Implement API Endpoints for Controls | [x] | VERIFIED | `backend/app/routes/compliance.py:21-98` |

| Implement API Endpoints for Risks, Business Processes, Regulatory Frameworks | [x] | VERIFIED | `backend/app/routes/compliance.py:100-358` |

| Implement Tenant Isolation with JWT | [x] | VERIFIED | `backend/app/routes/compliance.py` (tenant_id = user.id logic) |

| Develop and execute integration tests | [x] | VERIFIED | `backend/tests/test_compliance.py` |



**Summary:** 4 of 4 completed tasks verified.



### Test Coverage and Gaps

- **Coverage:** Full CRUD coverage for all 4 entities (Create, Read List, Read ID, Update, Delete).

- **Gaps:** None identified for MVP scope.



### Architectural Alignment

- **Tech Spec:** Aligned with `tech-spec-epic-1.md`.

- **Patterns:** Correctly uses `Depends(get_async_session)`, `Depends(current_active_user)`, and Pydantic models.



### Security Notes

- **Auth:** All endpoints properly secured with `user: User = Depends(current_active_user)`.

- **Isolation:** Explicit filters `filter(Entity.tenant_id == tenant_id)` applied on all queries.



### Best-Practices and References

- FastAPI Pagination used correctly.

- Async database sessions used correctly.



### Action Items



**Code Changes Required:**

- [ ] [Low] Refactor `tenant_id` logic when User model supports explicit organization/tenant association (Tech Debt) [file: `backend/app/routes/compliance.py`]



**Advisory Notes:**

- Note: Ensure `backend/tests/conftest.py` changes are committed as they fix general test infrastructure.
