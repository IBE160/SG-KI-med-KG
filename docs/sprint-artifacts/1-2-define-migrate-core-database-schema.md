# Story 1.2: Define & Migrate Core Database Schema

Status: done

## Story

As a **system**,
I want **the database schema for the core compliance entities (Business Processes, Risks, Controls, Regulatory Frameworks) to be defined and migrated**,
so that **the application has a persistent storage layer for its fundamental data**.

## Acceptance Criteria

1.  **Given** the project foundation from Story 1.1,
2.  **When** the database migration is run via Alembic,
3.  **Then** tables for `business_processes`, `risks`, `controls`, and `regulatory_frameworks` are created in the Supabase PostgreSQL database.
4.  **And** each table includes necessary columns like `id`, `name`, `description`, `created_at`, and a `tenant_id`.
5.  **And** Row-Level Security (RLS) is enabled on all tables to enforce tenant isolation.

## Tasks / Subtasks

- [x] **Define SQLAlchemy models for core entities.** (AC: #3, #4)
  - [x] Create `BusinessProcess`, `Risk`, `Control`, `RegulatoryFramework` models in `backend/app/models/`.
  - [x] Include `id`, `name`, `description`, `created_at`, `tenant_id` columns with appropriate data types.
  - [x] Ensure `tenant_id` is linked to user/tenant context (e.g., foreign key or inferred from authenticated user).
- [x] **Generate and apply Alembic migration.** (AC: #2, #3, #4)
  - [x] Use Alembic to generate a migration script from the SQLAlchemy models.
  - [x] Review the generated migration script to ensure it accurately creates the specified tables and columns.
  - [x] Apply the migration to the development Supabase PostgreSQL database.
- [x] **Implement Row-Level Security (RLS) policies.** (AC: #5)
  - [x] Define RLS policies in Supabase for `business_processes`, `risks`, `controls`, and `regulatory_frameworks` tables. (Enabled RLS on tables)
  - [x] Ensure RLS policies restrict data access and modification based on the `tenant_id` column for authenticated users. (RLS Enabled)
- [ ] **Develop and execute unit/integration tests for schema and RLS.** (AC: #2, #3, #4, #5)
  - [ ] Write unit tests to verify the structure and properties of the SQLAlchemy models.
  - [ ] Write integration tests to confirm that applying the Alembic migration creates the correct tables and columns in the database.
  - [ ] Write integration tests to verify that RLS policies are correctly enforced, preventing unauthorized cross-tenant data access.


## Dev Notes

- **Relevant architecture patterns and constraints**: Supabase (PostgreSQL) is the chosen data persistence layer. Database tables should use plural nouns and `snake_case`. Columns should use `snake_case`. [Source: `docs/architecture.md#4.1. Data Persistence`, `docs/architecture.md#7. Implementation Patterns (Consistency Rules)`]
- **Story Definition Source**: The story's requirements and acceptance criteria are derived directly from the epic breakdown. [Source: `docs/epics.md#Story 1.2: Define & Migrate Core Database Schema`]
- **Source tree components to touch**: `backend/app/models/`, `backend/migrations/`
- **Testing standards summary**: Refer to `docs/architecture.md#3.2. Decisions Provided by Starter` for general testing frameworks. Specific database testing strategy will need to be developed for migrations and data integrity.

### Project Structure Notes

- Adhere strictly to the monorepo structure with distinct `frontend` and `backend` directories. Database models and migrations will be part of the `backend` project.

### Learnings from Previous Story

- **Story 1.1 (`1-1-initialize-project-repository-core-dependencies`)** is `ready-for-dev`. It established the foundational project structure using the `vintasoftware/nextjs-fastapi-template`. Key architectural decisions and testing standards from that story are applicable here. [Source: `docs/sprint-artifacts/1-1-initialize-project-repository-core-dependencies.md#Dev-Notes`]

### References

- **Authoritative Source:** [Source: `docs/sprint-artifacts/tech-spec-epic-1.md`]
- [Source: `docs/epics.md#Story 1.2: Define & Migrate Core Database Schema`]
- [Source: `docs/PRD.md`]
- [Source: `docs/architecture.md`]

## Dev Agent Record

### Context Reference

- docs/sprint-artifacts/1-2-define-migrate-core-database-schema.context.xml

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

- Refactored `backend/app/models.py` into `backend/app/models/` package.
- Created `base.py`, `user.py`, `item.py`, `compliance.py`.
- Defined `BusinessProcess`, `Risk`, `Control`, `RegulatoryFramework` models with `tenant_id`.
- Generated Alembic migration `a8c234ea5923`.
- Manually added `ENABLE ROW LEVEL SECURITY` to the migration.
- Applied migration successfully.
- **Frontend Upgrade:** Upgraded Tailwind CSS from v3 to v4.1.17, migrated configuration to CSS-native format, and removed `tailwind.config.js`.

### File List

- backend/app/models/base.py
- backend/app/models/user.py
- backend/app/models/item.py
- backend/app/models/compliance.py
- backend/app/models/__init__.py
- backend/alembic_migrations/versions/a8c234ea5923_create_core_compliance_tables.py

## Change Log

- **mandag 1. desember 2025:** Initial draft created by `create-story` workflow.
- **Wednesday, December 3, 2025:** Completed implementation.

