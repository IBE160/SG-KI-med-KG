# Epic Technical Specification: {{epic_title}}

Date: {{date}}
Author: {{user_name}}
Epic ID: {{epic_id}}
Status: Draft

---

## Overview

This document provides the technical specification for Epic 1: Foundational Setup & Core Compliance Data Model. The primary goal of this epic is to establish the project's technical foundation by initializing the repository from the chosen `vintasoftware/nextjs-fastapi-template`, defining the core database schema for compliance entities (Business Processes, Risks, Controls, Regulatory Frameworks), implementing the necessary API endpoints for CRUD operations, and building a basic UI for data management. This epic covers FR-2 (Core Data CRUD) and is a prerequisite for all subsequent feature development.

## Objectives and Scope

**In Scope:**
*   Initializing the project repository from the `vintasoftware/nextjs-fastapi-template`.
*   Installing all core dependencies (`uv`, `pnpm`).
*   Configuring environment variables for Supabase, OpenAI, and SendGrid.
*   Defining and migrating the database schema for `business_processes`, `risks`, `controls`, and `regulatory_frameworks` using SQLAlchemy and Alembic.
*   Enabling Row-Level Security (RLS) for tenant isolation on core tables.
*   Enabling the `pgvector` extension in Supabase.
*   Implementing and testing FastAPI endpoints (GET, POST, PUT, DELETE) for all core data entities.
*   Building basic data management UI pages in Next.js using Shadcn UI components for all core entities.

**Out of Scope:**
*   User registration and authentication (covered in Epic 2).
*   AI-powered features (covered in Epic 3).
*   Role-specific dashboards and real-time updates (covered in Epic 4).
*   Compliance mapping UI (covered in Epic 5).

## System Architecture Alignment

This epic directly implements the foundational decisions outlined in the Architecture Document. It utilizes the `vintasoftware/nextjs-fastapi-template` as decided. The database schema will be created in the chosen **Supabase (PostgreSQL)** instance, and the API endpoints will be built in the **FastAPI** backend, preparing for deployment to **Railway**. The frontend UI will be built in **Next.js**, preparing for deployment to **Vercel**. All naming conventions and API structure rules defined in the architecture document will be strictly followed. The setup of the `pgvector` extension is a direct prerequisite for the AI work in Epic 3.

## Detailed Design

### Services and Modules

| Service/Module | Responsibilities | Inputs | Outputs | Owner |
| :--- | :--- | :--- | :--- | :--- |
| **`backend.app.api.v1`** | Exposes RESTful endpoints for core entities. | HTTP Requests | JSON Responses | `dev` |
| **`backend.app.crud`** | Handles database session management and query logic. | Pydantic Schemas | SQLAlchemy Models | `dev` |
| **`backend.app.models`** | Defines the SQLAlchemy ORM models. | - | Python Classes | `dev` |
| **`backend.app.schemas`**| Defines the Pydantic data schemas for API validation. | - | Python Classes | `dev` |
| **`frontend.app`** | Renders the Next.js UI pages and components. | User Interactions | HTML/CSS/JS | `dev` |
| **`frontend.services`**| Provides typed client for making API calls to the backend. | Function Calls | Promises with typed data | `dev` |

### Data Models and Contracts

The core data models will be defined in `backend/app/models/`.

**Control Model (`controls` table):**
```sql
CREATE TABLE controls (
  id SERIAL PRIMARY KEY,
  tenant_id UUID NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  owner_id UUID REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```
*Similar schemas will be created for `risks`, `business_processes`, and `regulatory_frameworks`.*

### APIs and Interfaces

The following RESTful API endpoints will be created in the FastAPI backend under the `/api/v1/` prefix.

**Controls API (`/api/v1/controls`):**
*   `GET /`: List all controls for the tenant.
*   `POST /`: Create a new control.
*   `GET /{control_id}`: Retrieve a single control.
*   `PUT /{control_id}`: Update a control.
*   `DELETE /{control_id}`: Delete a control.

*Similar endpoints will be created for `risks`, `business_processes`, and `regulatory_frameworks`.*

### Workflows and Sequencing

1.  **DB Migration:** The Alembic migration script for the core schema must be run first.
2.  **API Implementation:** The CRUD APIs for all core entities can be developed in parallel.
3.  **Frontend Implementation:** The UI pages for managing each core entity can be developed in parallel, once the corresponding APIs are available.

## Non-Functional Requirements

### Performance

*   API response times for all CRUD operations must be < 500ms.
*   The initial load time for the data management pages (LCP) must be < 2.5s.

### Security

*   All API endpoints must enforce tenant isolation via RLS based on the JWT token.
*   SQL injection will be prevented by using the SQLAlchemy ORM.
*   Input data will be validated using Pydantic schemas.

### Reliability/Availability

*   The API and frontend services will be deployed with health checks to ensure they are running.
*   Database backups are managed by Supabase.

### Observability

*   FastAPI will be configured to log all API requests, including path, status code, and response time.
*   Frontend will log any critical errors to the browser console.

## Dependencies and Integrations

*   **`vintasoftware/nextjs-fastapi-template`**: Core project structure.
*   **`SQLAlchemy`**: ORM for database interaction.
*   **`Alembic`**: Database migrations.
*   **`Pydantic`**: Data validation.
*   **`Shadcn/UI`**: Frontend component library.
*   **`Supabase`**: Database, Auth, Storage.

## Acceptance Criteria (Authoritative)

1.  A new repository is created from the `vintasoftware/nextjs-fastapi-template`.
2.  All dependencies are installed using `uv` and `pnpm`.
3.  The application runs successfully via `docker compose up`.
4.  The `pgvector` extension is enabled in the Supabase database.
5.  Alembic migration creates tables for `business_processes`, `risks`, `controls`, and `regulatory_frameworks`.
6.  All core tables have RLS enabled for tenant isolation.
7.  CRUD API endpoints for `controls` return correct status codes and data.
8.  CRUD API endpoints for `risks` return correct status codes and data.
9.  CRUD API endpoints for `business_processes` return correct status codes and data.
10. CRUD API endpoints for `regulatory_frameworks` return correct status codes and data.
11. Admin can view a list of controls in the UI.
12. Admin can create a new control via a UI modal.
13. Admin can edit an existing control via the UI.
14. Admin can delete a control via the UI.

## Traceability Mapping

| AC | Spec Section(s) | Component(s)/API(s) | Test Idea |
| :- | :--- | :--- | :--- |
| 1-4| Detailed Design | Project Init | Manual verification |
| 5-6| Data Models | `backend/migrations`| Pytest for model creation |
| 7-10| APIs and Interfaces| `backend/app/api/v1` | Pytest for API endpoints |
| 11-14| Detailed Design | `frontend/app/(dashboard)/admin` | E2E test with Playwright |

## Risks, Assumptions, Open Questions

*   **Risk:** The `vintasoftware/nextjs-fastapi-template` may have breaking changes. **Mitigation:** Pin dependency versions.
*   **Assumption:** The developer has the necessary permissions to configure Supabase.
*   **Question:** What are the exact fields required for each core data model beyond `id`, `name`, `description`?

### Post-Review Follow-ups (AI)



**Epic 1: Foundational Setup & Core Compliance Data Model - Follow-ups**



*   - [ ] [AI-Review][High] **Implement RLS Policies:** Add `op.execute("CREATE POLICY ...")` statements to the migration file for each table to define actual access rules (AC #5). [file: `backend/alembic_migrations/versions/a8c234ea5923_create_core_compliance_tables.py`] (Story 1.2)

*   - [ ] [AI-Review][High] **Write Tests:** Implement unit tests for models and integration tests for DB persistence. [file: `backend/tests/test_compliance_models.py`] (Story 1.2)

*   - [ ] [AI-Review][Low] **Refactor Tenant ID:** Refactor `tenant_id` logic when User model supports explicit organization/tenant association (Tech Debt). [file: `backend/app/routes/compliance.py`] (Story 1.3)

*   - [ ] [AI-Review][Low] **Run Playwright Tests:** Ensure `npx playwright test` is run locally or in CI to validate the authored E2E tests. (Story 1.4)

*   - [ ] [AI-Review][Low] **Error Toast:** Consider adding a toast notification library (like `sonner` or `react-hot-toast`) for better user feedback on success/failure actions, replacing or augmenting the inline alerts. (Story 1.4)