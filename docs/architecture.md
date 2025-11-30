# ibe160 Decision Architecture Document

**Version:** 1.0
**Date:** 2025-11-30
**Status:** Complete
**Author:** Winston (Architect AI)

---

## 1. Executive Summary

This document outlines the complete technical architecture for the **ibe160 Risk Control Matrix**, a multi-tenant SaaS platform designed to provide AI-powered GRC (Governance, Risk, and Compliance) capabilities. The architecture is designed to be scalable, secure, and maintainable, directly supporting the core business goal of reducing audit preparation time and providing real-time risk visibility.

The chosen architecture is a **decoupled, full-stack application** using a Next.js frontend and a FastAPI (Python) backend. This approach allows for specialized hosting and independent scaling. The core data platform is **Supabase**, which provides the PostgreSQL database, authentication, file storage, real-time updates, and vector database capabilities, simplifying the stack and accelerating development. The architecture is defined by a series of key decisions designed to ensure consistency and prevent conflicts during AI-assisted implementation.

## 2. Project Context Understanding

I'm reviewing your project documentation for ibe160.
I see 5 epics with 15 total stories.
I also found your UX specification which defines the user experience requirements.

Key aspects I notice:
- The core functionality is an AI-powered gap analysis for GRC, acting as an "AI Legal Specialist" in a multi-tenant SaaS application.
- Critical NFRs include a robust and immutable audit trail, data security with encryption, multi-tenancy with RLS, and a Human-in-the-Loop (HITL) validation workflow.
- The UX is desktop-first, centered on an "Action-Oriented Hub" dashboard, and features a novel two-stage "AI Review Mode" for triaging and approving AI suggestions.
- The unique challenge is building trust in the AI's "legal specialist" persona and ensuring its suggestions are seamlessly integrated into an accountable, human-validated workflow.

This will help me guide you through the architectural decisions needed to ensure AI agents implement this consistently.

## 3. Foundational Decisions

### 3.1. Starter Template Decision

Based on the project's technical specifications, the `vintasoftware/nextjs-fastapi-template` has been chosen as the foundational starter template.

**Project Initialization Note:** The first implementation story will be to initialize the project repository. This is a multi-step process:
1. Create a new repository from the `vintasoftware/nextjs-fastapi-template`.
2. Clone the new repository.
3. Install dependencies (`uv`, `pnpm`).
4. Configure environment variables (`.env`).
5. Run the application using the provided `docker compose` commands.

### 3.2. Decisions Provided by Starter

The following architectural decisions are provided by the starter and will be marked as such in our decision log:

- **Language/TypeScript:** End-to-end type safety with TypeScript for the frontend and Python with Pydantic for the backend.
- **Styling Solution:** Tailwind CSS via the integrated Shadcn/UI component library.
- **Testing Framework:** Pytest for the backend. Pre-commit hooks are included for static checks.
- **Linting/Formatting:** Provided by pre-commit hooks.
- **Build Tooling:** A combination of `uv` (for Python), `pnpm` (for Node.js), `Docker Compose`, and `make`.
- **Project Structure:** A monorepo with distinct `frontend` and `backend` directories.
- **Authentication:** A production-ready system using `fastapi-users`.

## 4. Architectural Decision Records

### 4.1. Data Persistence

- **Category:** `data_persistence`
- **Decision:** **Supabase (PostgreSQL)**
- **Version:** `@supabase/supabase-js v2.86.0` (Verified on 2025-11-30)
- **Affects:** All Epics.
- **Rationale:** This choice was confirmed from the project proposal. It provides a robust, relational database suitable for the structured and interconnected nature of GRC data. Furthermore, the Supabase platform provides a suite of integrated tools (Authentication, File Storage, Real-time) that are required by the project, reducing complexity and accelerating development.
- **Cascading Implications:** This decision strongly suggests the use of Supabase Storage for file uploads and Supabase Realtime for live updates, which will be our subsequent decisions.

### 4.2. Deployment Targets

- **Category:** `deployment_target`
- **Decision:** **Vercel (Frontend), Railway (Backend)**
- **Version:** N/A (Cloud Services, status confirmed 2025-11-30)
- **Affects:** All Epics.
- **Rationale:** This choice was confirmed from the project proposal. This "best-of-breed" strategy uses specialized hosts for the frontend and backend, ensuring optimal performance, reliability, and scalability. Vercel is purpose-built for Next.js frontends. Railway's persistent server environment is critical for the long-running AI tasks required by the backend, mitigating the timeout risks associated with serverless-only platforms.
- **Cascading Implications:** This reinforces the decoupled nature of the frontend and backend, influencing CI/CD pipeline design to manage two separate deployment targets.

### 4.3. AI & Vector Database

- **Category:** `ai_application`
- **Decision:** **OpenAI GPT-4 (LLM), pgvector on Supabase (Vector Database)**
- **Version:** `gpt-4-turbo` (or latest at implementation), `pgvector` (integrated with Supabase)
- **Affects:** Epic 3 (AI-Powered Gap Analysis & Auditing)
- **Rationale:** Aligns with the project proposal. GPT-4 is the leading model for the complex legal reasoning required. Using `pgvector` with our existing Supabase database is a highly efficient and cost-effective choice, as it leverages our chosen infrastructure and simplifies the overall architecture.
- **Cascading Implications:** The backend will require a library for interacting with the OpenAI API (e.g., `Pydantic-AI` as proposed). The initial database migration (Story 1.2) must include enabling the `pgvector` extension in Supabase. Secure management of OpenAI API keys is required.

### 4.4. Real-time Updates

- **Category:** `real_time`
- **Decision:** **Supabase Realtime**
- **Version:** Included in `@supabase/supabase-js v2.86.0`
- **Affects:** Epic 4 (Real-Time Risk Monitoring & Assessment)
- **Rationale:** This choice leverages our existing Supabase infrastructure and directly fulfills the requirement for live dashboard updates (FR-7). It is the most efficient and integrated method, pushing database changes directly to clients without needing a complex, self-managed WebSocket layer.
- **Cascading Implications:** The frontend application will use the Supabase JS client to subscribe to database changes. No significant backend changes are required, as the notifications are handled by the Supabase infrastructure.

### 4.5. File Storage

- **Category:** `file_storage`
- **Decision:** **Supabase Storage**
- **Version:** Included in `@supabase/supabase-js v2.86.0`
- **Affects:** Epic 3 (AI-Powered Gap Analysis & Auditing)
- **Rationale:** This leverages our existing Supabase infrastructure and provides a secure, S3-compatible, and highly integrated solution for the document uploads required by FR-4. It simplifies the architecture and avoids the cost and complexity of a separate third-party storage provider.
- **Cascading Implications:** The backend will need logic to generate secure upload URLs for the client. The frontend will use the Supabase client library to handle the file upload.

### 4.6. Background Jobs

- **Category:** `background_jobs`
- **Decision:** **Celery with Redis**
- **Version:** `Celery v5.3+`, `Redis v7+`
- **Affects:** Epic 3 (AI-Powered Gap Analysis & Auditing)
- **Rationale:** AI analysis of documents can be a long-running process. To ensure the user interface remains responsive, these tasks must be handled asynchronously. Celery is the industry-standard, robust, and scalable task queue for Python. Redis is a fast, reliable message broker that pairs perfectly with Celery. This provides a powerful system for managing background work.
- **Cascading Implications:** A Redis instance will need to be provisioned (can be done on Railway). The backend application will be configured as a Celery producer, and separate Celery worker processes will need to be run and deployed on Railway.

### 4.7. Email Service

- **Category:** `email`
- **Decision:** **SendGrid**
- **Version:** N/A (Cloud Service)
- **Affects:** Epic 2 (User Identity & Access Management), and post-MVP notification features.
- **Rationale:** This choice is specified in the `proposal.md`. SendGrid is a mature, reliable, and scalable platform for delivering transactional emails like registration confirmations and password resets.
- **Cascading Implications:** The backend will require the SendGrid client library and secure management of the SendGrid API key.

## 5. Project Structure & Boundaries

The project will be organized as a monorepo, following the structure provided by the chosen starter template.

```
/
├── .github/                # CI/CD workflows (e.g., deploy frontend to Vercel, backend to Railway)
├── backend/                # FastAPI Application
│   ├── app/                # Core application logic
│   │   ├── api/            # API endpoints (routers)
│   │   │   └── v1/
│   │   ├── core/           # Configuration, security
│   │   ├── crud/           # Database interaction logic
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic data schemas
│   │   └── services/       # Business logic (e.g., AI analysis service)
│   ├── migrations/         # Alembic database migrations
│   ├── tasks/              # Celery background tasks
│   └── tests/              # Pytest tests
├── frontend/               # Next.js Application
│   ├── app/                # App Router directory structure
│   │   ├── (auth)/         # Route group for auth pages (login, register)
│   │   ├── (dashboard)/    # Route group for protected dashboard pages
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx    # Main dashboard
│   │   └── layout.tsx      # Root layout
│   ├── components/         # Reusable React components (Shadcn/UI)
│   │   ├── ui/             # Unmodified Shadcn components
│   │   └── custom/         # Custom-built components (e.g., AI Review Mode)
│   ├── lib/                # Helper functions, Supabase client
│   ├── hooks/              # Custom React hooks
│   └── services/           # Auto-generated API client from backend schema
└── ...                     # Root config files (.gitignore, package.json, etc.)
```

### Epic-to-Architecture Mapping
- **Epic 1 (Foundational Setup):** Lives in `backend/app/models`, `backend/migrations`, `backend/app/api/v1`, and `frontend/app/(dashboard)/admin`.
- **Epic 2 (IAM):** Lives in `backend/app/core/security.py`, `frontend/app/(auth)`, and Supabase Auth configuration.
- **Epic 3 (AI & Auditing):** Lives in `backend/app/services/ai_service.py`, `backend/tasks/analysis.py`, `frontend/components/custom/ai-review-mode`, and the database audit log implementation.
- **Epic 4 (Monitoring & Assessment):** Lives in `frontend/app/(dashboard)` and utilizes `Supabase Realtime` subscriptions in `frontend/hooks`.
- **Epic 5 (Mapping & Reporting):** Lives in `backend/app/api/v1/mapping.py` and `frontend/app/(dashboard)/reports`.

## 6. Implementation Patterns (Consistency Rules)

To ensure consistency across code written by different developers or AI agents, the following patterns are **MANDATORY**.

### Naming Conventions
- **API Endpoints:** Plural nouns, kebab-case (e.g., `/api/v1/business-processes`).
- **Database Tables:** Plural nouns, snake_case (e.g., `business_processes`).
- **Database Columns:** snake_case (e.g., `created_at`, `process_owner_id`).
- **React Components (TSX files):** PascalCase (e.g., `UserCard.tsx`).
- **General Variables/Functions:** camelCase (e.g., `const userProfile = ...`).

### API Structure
- **Versioning:** All API routes will be prefixed with `/api/v1/`.
- **Response Format:** All successful `GET`, `PUT`, `POST` responses will return a JSON object directly. `DELETE` will return a `204 No Content`.
- **Error Format:** Errors will follow a consistent structure: `{ "detail": "Error message here" }`. FastAPI handles this by default.
- **Authentication:** All protected routes will expect a JWT in the `Authorization: Bearer <token>` header.

### State Management (Frontend)
- **Global State:** **Zustand** will be used for minimal global state (e.g., logged-in user profile).
- **Server State:** **React Query** (or a similar data-fetching library) will be the primary tool for managing server state, caching, and mutations. Do not store server data in Zustand.
- **Local State:** `useState` and `useReducer` for component-level state.

### Code Style & Formatting
- The pre-commit hooks provided by the starter template (which include `black` for Python and `prettier` for TypeScript/JSON) will be the single source of truth for code style. All code **must** pass these checks before being committed.

## 7. Final Validation and Next Steps

The architecture defined in this document is coherent and complete for the MVP. All functional and non-functional requirements from the PRD are addressed by the chosen technologies and patterns. The combination of the `vintasoftware` starter template with the Supabase ecosystem provides a powerful, modern, and efficient foundation for development.

### Next Steps
1. **Implementation:** The development team can now begin work, starting with **Epic 1, Story 1.1**: Initialize the project repository using the chosen starter template.
2. **Backlog Refinement:** The PM and Architect will refine the user stories in `epics.md` to include specific technical details from this architecture document.
3. **Workflow Status Update:** This `create-architecture` workflow is now complete. The `bmm-workflow-status.yaml` file should be updated to reflect this.

---
_This document serves as the primary technical blueprint for the ibe160 project._
