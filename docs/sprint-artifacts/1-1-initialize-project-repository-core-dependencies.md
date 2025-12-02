# Story 1.1: Initialize Project Repository & Core Dependencies

Status: ready-for-dev

## Story

As a **development team**,
I want **to initialize the project from the chosen `vintasoftware/nextjs-fastapi-template`**,
so that **we have a stable and consistent foundation for building the application, aligned with architectural decisions**.

## Acceptance Criteria

1. A new repository is created from the `vintasoftware/nextjs-fastapi-template`.
2. All dependencies are installed using `uv` and `pnpm`.
3. Environment variables (`.env`) are configured for Supabase, OpenAI, and SendGrid.
4. The application runs successfully via `docker compose up`.
5. The `pgvector` extension is enabled in the Supabase database.

## Tasks / Subtasks

- [ ] **Setup Repository** (AC: #1)
  - [ ] Create a new GitHub repository using the `vintasoftware/nextjs-fastapi-template`.
  - [ ] Clone the new repository to the local development environment.
  - [ ] **Test:** Manually verify that the new repository exists on GitHub and is a correct fork of the template.
- [ ] **Install Dependencies** (AC: #2)
  - [ ] Run `pnpm install` in the `frontend` directory.
  - [ ] Run `uv pip install -r requirements.txt` in the `backend` directory.
  - [ ] **Test:** Check for the presence of `node_modules` and the `uv` virtual environment, and ensure no installation errors were reported.
- [ ] **Configure Environment** (AC: #3)
  - [ ] Create a `.env` file in the root directory.
  - [ ] Add placeholders for `SUPABASE_URL`, `SUPABASE_KEY`, `OPENAI_API_KEY`, `SENDGRID_API_KEY`.
  - [ ] **Test:** Manually verify that the `.env` file is present and contains the correct placeholder keys.
- [ ] **Verify Application** (AC: #4)
  - [ ] Run `docker compose up --build`.
  - [ ] Access the frontend at `http://localhost:3000` and the backend docs at `http://localhost:8000/docs`.
  - [ ] **Test:** Confirm that the frontend loads without errors and the backend API documentation is accessible.
- [ ] **Configure Database** (AC: #5)
  - [ ] Log in to the Supabase dashboard.
  - [ ] Navigate to the SQL Editor.
  - [ ] Execute `CREATE EXTENSION IF NOT EXISTS pgvector;` to enable the `pgvector` extension.
  - [ ] **Test:** Run `SELECT * FROM pg_extension WHERE extname = 'pgvector';` in the Supabase SQL Editor to confirm the extension is installed.

## Dev Notes

This story is foundational and sets up the entire project structure. It is critical that all steps are followed precisely as defined in the Architecture Document. No application logic is to be written in this story.

- **Relevant architecture patterns and constraints**: The project follows a decoupled, full-stack application model with a Next.js frontend and a FastAPI backend. All development must adhere to the structure provided by the `vintasoftware/nextjs-fastapi-template`. [Source: `docs/architecture.md#3.1. Starter Template Decision`]
- **Source tree components to touch**: This story primarily involves root-level configuration (`.env`, `docker-compose.yml`) and running setup commands. No application code will be modified.
- **Testing standards summary**: The starter template includes pre-commit hooks for linting and formatting. Ensure they are active. Backend testing will use `Pytest`. [Source: `docs/architecture.md#3.2. Decisions Provided by Starter`]

### Project Structure Notes

- Adhere strictly to the monorepo structure with distinct `frontend` and `backend` directories.
- No conflicts are expected as this is the initial setup.

### Learnings from Previous Story
First story in epic - no predecessor context

### References

- [Source: `docs/epics.md#Epic 1: Foundational Setup & Core Compliance Data Model`]
- [Source: `docs/architecture.md#3. Foundational Decisions`]
- [Source: `docs/sprint-artifacts/tech-spec-epic-1.md`]

## Dev Agent Record

### Context Reference

- docs/sprint-artifacts/1-1-initialize-project-repository-core-dependencies.context.xml

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

- **Plan for Task 1 (Setup Repository):**
  1. Since I am in an existing git repo `SG-KI-med-KG`, I will treat this as the target repository.
  2. I will fetch the `vintasoftware/nextjs-fastapi-template` code into this repository.
  3. Command: `git remote add template https://github.com/vintasoftware/nextjs-fastapi-template.git`
  4. Command: `git pull template main --allow-unrelated-histories`
  5. Verify `frontend` and `backend` directories exist.

### Completion Notes List

### File List

## Change Log

- **2025-12-01:** Initial draft created by `create-story` workflow.
