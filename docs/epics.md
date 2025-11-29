# ibe160 - Epic Breakdown

**Author:** BIP
**Date:** 2025-11-29
**Project Level:** High
**Target Scale:** Enterprise

---

## Overview

This document provides the complete epic and story breakdown for ibe160, decomposing the requirements from the [PRD](./PRD.md) into implementable stories.

**Living Document Notice:** This is the initial version. It will be updated after UX Design and Architecture workflows add interaction and technical details to stories.

Here is the proposed epic structure based on the functional requirements. This structure is designed to deliver value incrementally, with each epic representing a significant piece of user-facing functionality.

- **Epic 1: Foundational Setup & Core Compliance Data Model:** Establishes the project's technical foundation and creates the core data structures for managing compliance information.
- **Epic 2: User Identity & Access Management (IAM):** Enables secure user access and enforces role-based permissions for Admins, BPOs, Executives, and General Users.
- **Epic 3: AI-Powered Gap Analysis & Auditing:** Delivers the core "AI Legal Specialist" by enabling document analysis, human-in-the-loop validation, and a complete audit trail.
- **Epic 4: Real-Time Risk Monitoring & Assessment:** Provides real-time dashboards tailored to user roles and the primary workflow for Business Process Owners to assess controls.
- **Epic 5: Advanced Compliance Mapping & Reporting:** Enables the central many-to-many compliance mapping feature, allowing controls to be linked to regulatory requirements.


---

## Functional Requirements Inventory

Here is the complete list of functional requirements extracted from the PRD:

-   **FR-1: Role-Based Access Control:** The system must support four distinct user roles within each tenant: Admin, Business Process Owner (BPO), Executive, and General User.
-   **FR-2: Core Data CRUD:** Authorized users (primarily Admins) must be able to Create, Read, Update, and Delete the core data entities: Business Processes, Risks, Controls, and Regulatory Frameworks.
-   **FR-3: Compliance Mapping:** The system must allow many-to-many mapping between controls and the specific requirements within regulatory frameworks.
-   **FR-4: AI-Assisted Document Analysis:** An Admin must be able to upload a regulatory document (e.g., in PDF or text format). The system will use the AI to parse the document and present a list of suggested risks and controls based on its content.
-   **FR-5: Human-in-the-Loop (HITL) Validation:** All AI-generated suggestions must be presented to a qualified user for explicit approval or rejection before they become active data in the system.
-   **FR-6: Role-Specific Dashboards:** The application must present a tailored dashboard experience for each user role upon login.
-   **FR-7: Real-Time Status Updates:** Changes in the status of a control or risk must be reflected on all relevant dashboards in near real-time.
-   **FR-8: Immutable Audit Trail:** All actions that create, modify, or delete critical compliance data (including risks, controls, and assessments) must be recorded in an immutable audit log.
-   **FR-9: Streamlined Control Assessment:** The system must provide a simple, intuitive interface for a BPO to assess an assigned control. This workflow will be the primary interaction for all BPO users.

---

## FR Coverage Map

This map shows which Functional Requirements (FRs) are addressed by each proposed epic. Every requirement from the PRD is covered.

-   **Epic 1: Foundational Setup & Core Compliance Data Model**
    -   Covers: **FR-2** (Core Data CRUD)
-   **Epic 2: User Identity & Access Management (IAM)**
    -   Covers: **FR-1** (Role-Based Access Control)
-   **Epic 3: AI-Powered Gap Analysis & Auditing**
    -   Covers: **FR-4** (AI-Assisted Document Analysis), **FR-5** (Human-in-the-Loop Validation), **FR-8** (Immutable Audit Trail)
-   **Epic 4: Real-Time Risk Monitoring & Assessment**
    -   Covers: **FR-6** (Role-Specific Dashboards), **FR-7** (Real-Time Status Updates), **FR-9** (Streamlined Control Assessment)
-   **Epic 5: Advanced Compliance Mapping & Reporting**
    -   Covers: **FR-3** (Compliance Mapping)


---

## Epic 1: Foundational Setup & Core Compliance Data Model

**Goal:** To establish the project's technical foundation and create the core data structures for managing compliance information. This is a necessary prerequisite for all other features.

### Story 1.1: Initialize Project Repository & Core Dependencies
As a **development team**,
I want **a standardized project structure with all core dependencies (Next.js, FastAPI, Supabase client) installed and configured**,
So that **we have a stable and consistent foundation for building the application**.

**Acceptance Criteria:**
**Given** a new project environment,
**When** the initialization script is run,
**Then** a monorepo is created with separate `frontend` (Next.js) and `backend` (FastAPI) directories.
**And** Supabase client is installed and configured in the frontend.
**And** core backend dependencies (FastAPI, SQLAlchemy, Alembic, Pydantic-AI) are installed.
**And** basic "hello world" endpoints are functional for both frontend and backend.

**Prerequisites:** None
**Technical Notes:** This story sets up the entire repository and CI/CD pipeline foundation. It should include basic linting, formatting, and environment variable setup.

### Story 1.2: Define & Migrate Core Database Schema
As a **system**,
I want **the database schema for the core compliance entities (Business Processes, Risks, Controls, Regulatory Frameworks) to be defined and migrated**,
So that **the application has a persistent storage layer for its fundamental data**.

**Acceptance Criteria:**
**Given** the project foundation from Story 1.1,
**When** the database migration is run via Alembic,
**Then** tables for `business_processes`, `risks`, `controls`, and `regulatory_frameworks` are created in the Supabase PostgreSQL database.
**And** each table includes necessary columns like `id`, `name`, `description`, `created_at`, and a `tenant_id`.
**And** Row-Level Security (RLS) is enabled on all tables to enforce tenant isolation.

**Prerequisites:** Story 1.1
**Technical Notes:** The schema should be defined using SQLAlchemy models. Migrations will be managed by Alembic.

### Story 1.3: Implement API Endpoints for Core Data CRUD
As an **Admin**,
I want **to be able to Create, Read, Update, and Delete the core compliance entities via the API**,
So that **the frontend has a secure and reliable way to manage the foundational data**.

**Acceptance Criteria:**
**Given** the database schema from Story 1.2 and an authenticated Admin user,
**When** a POST request is sent to `/api/v1/controls` with valid data,
**Then** a new control is created in the database and a 201 status is returned.
**And** GET (list and by ID), PUT, and DELETE endpoints are functional for `controls`, `risks`, `business_processes`, and `regulatory_frameworks`.
**And** all API endpoints enforce tenant isolation based on the authenticated user's JWT token, failing with a 404 if a resource from another tenant is requested.

**Prerequisites:** Story 1.2
**Technical Notes:** The FastAPI backend will house these endpoints. Authentication will be handled by Supabase, with the JWT passed in the Authorization header.

### Story 1.4: Build Basic UI for Managing Core Data
As an **Admin**,
I want **a basic user interface to Create, Read, Update, and Delete the core compliance entities**,
So that **I can manage the foundational data of the system through the web application**.

**Acceptance Criteria:**
**Given** the API endpoints from Story 1.3,
**When** I navigate to the "/admin/controls" page,
**Then** I see a data table (using Shadcn UI components) listing all existing controls for my tenant.
**And** the table has "Create," "Edit," and "Delete" buttons.
**And** clicking "Create" opens a modal form to add a new control.
**And** similar UI pages and functionality exist for `risks`, `business_processes`, and `regulatory_frameworks`.

**Prerequisites:** Story 1.3
**Technical Notes:** This will be built in the Next.js frontend, utilizing the configured Supabase client to make authenticated API calls to the FastAPI backend.

---

## Epic 2: User Identity & Access Management (IAM)

**Goal:** Enable secure user access and enforce role-based permissions, ensuring that users can only see and do what their roles permit.

### Story 2.1: Implement User Registration & Login (Email/Password)
As a **new user**,
I want **to securely register for an account and log in using email and password**,
So that **I can access the application's features as an authenticated user**.

**Acceptance Criteria:**
**Given** I am on the registration page,
**When** I provide a valid email and password (meeting complexity requirements),
**Then** my account is created, and I receive an email verification link.
**And** after verifying my email, I can log in successfully.
**And** upon login, I am assigned the "General User" role by default within a tenant.

**Prerequisites:** Epic 1 (Core infrastructure, API endpoints).
**Technical Notes:** Utilize Supabase Auth for user management. Implement robust password hashing and email verification.

### Story 2.2: Implement Role-Based Access Control (RBAC)
As an **Admin**,
I want **to manage user roles (Admin, BPO, Executive, General User) within my tenant**,
So that **I can control access to features and data according to defined permissions**.

**Acceptance Criteria:**
**Given** I am logged in as an Admin,
**When** I access the user management interface,
**Then** I can change a user's role to Admin, BPO, Executive, or General User.
**And** the system enforces the permissions defined in the PRD for each role (e.g., General User cannot see Admin features).
**And** user roles are persisted and retrieved correctly upon login.

**Prerequisites:** Story 2.1.
**Technical Notes:** Implement middleware or decorators on API endpoints to check user roles based on JWT claims. Frontend dynamically renders UI elements based on user role.

---

## Epic 3: AI-Powered Gap Analysis & Auditing

**Goal:** Deliver the core "magic" of the product by enabling the AI to analyze documents and support a full audit cycle.

### Story 3.1: Implement Document Upload for AI Analysis
As an **Admin**,
I want **to upload regulatory documents (PDF/text) to the system**,
So that **the AI can analyze them for potential risks and controls**.

**Acceptance Criteria:**
**Given** I am logged in as an Admin and navigate to the document upload section,
**When** I upload a PDF or text file,
**Then** the document is securely stored, and its content is extracted for AI processing.
**And** I receive immediate feedback that the document has been received for analysis.

**Prerequisites:** Epic 1 (Core infrastructure, data storage).
**Technical Notes:** Implement secure file storage (e.g., Supabase Storage). Backend service (FastAPI) handles file reception and passes content to AI processing queue.

### Story 3.2: Integrate AI for Document Analysis & Suggestion Generation
As a **system**,
I want **to use AI (LLM) to analyze uploaded regulatory documents**,
So that **I can generate suggestions for risks and controls**.

**Acceptance Criteria:**
**Given** a regulatory document has been uploaded (Story 3.1),
**When** the AI analysis process completes,
**Then** the system presents a list of AI-generated suggestions for risks and controls relevant to the document's content.
**And** each suggestion includes a rationale, referencing specific clauses from the document.
**And** suggestions are formatted as structured data (using Pydantic-AI).

**Prerequisites:** Story 3.1.
**Technical Notes:** Implement Pydantic-AI for structured LLM output. Integrate with OpenAI GPT-4 (or similar LLM). Define clear prompts for "AI Legal Specialist" persona.

### Story 3.3: Build Human-in-the-Loop (HITL) Validation Interface
As a **Compliance Officer**,
I want **to review and explicitly approve or reject AI-generated suggestions for risks and controls**,
So that **I maintain oversight and ensure accuracy before they become active in the system**.

**Acceptance Criteria:**
**Given** AI-generated suggestions are available (Story 3.2),
**When** I access the HITL validation interface,
**Then** I see a clear list of suggestions, visually distinct from verified data.
**And** for each suggestion, there are "Approve" and "Reject" buttons.
**And** approving a suggestion adds it to the active `risks` or `controls` library (FR-2).
**And** rejecting a suggestion removes it from the pending list and optionally allows me to provide feedback.

**Prerequisites:** Story 3.2.
**Technical Notes:** Frontend development for the HITL interface. Backend endpoints to handle approval/rejection logic.

### Story 3.4: Implement Immutable Audit Trail
As a **system**,
I want **to automatically record all critical actions (CRUD on compliance data, AI suggestion approval/rejection) in an immutable audit log**,
So that **there is a comprehensive and verifiable history for compliance audits**.

**Acceptance Criteria:**
**Given** any critical action occurs (e.g., control creation, risk update, AI suggestion approved),
**When** the action is completed,
**Then** an entry is added to an `audit_log` table, capturing who, what, when, and the change details.
**And** audit log entries are read-only and cannot be modified or deleted.
**And** the audit log is accessible for review (e.g., via a dedicated interface or export).

**Prerequisites:** Epic 1 (Core data model), Epic 2 (User authentication).
**Technical Notes:** Implement database triggers or application-level logging for audit events.

---

## Epic 4: Real-Time Risk Monitoring & Assessment

**Goal:** Provide users with real-time visibility into the organization's risk posture and enable the core control assessment workflow.

### Story 4.1: Develop Role-Specific Dashboards
As a **user**,
I want **a tailored dashboard experience upon login**,
So that **I immediately see the most relevant information and actions for my role**.

**Acceptance Criteria:**
**Given** I am logged in with a specific role (Admin, BPO, Executive, General User),
**When** I land on the dashboard,
**Then** the content and layout of the dashboard are customized to my role (e.g., Executive sees high-level risk metrics, BPO sees pending assessments).
**And** the dashboard loads quickly (LCP < 2.5s).

**Prerequisites:** Epic 2 (RBAC), Epic 1 (Core Data CRUD for metrics).
**Technical Notes:** Frontend conditional rendering based on user role. Utilize Recharts for data visualization. Backend endpoints providing role-specific data feeds.

### Story 4.2: Implement Real-Time Status Updates
As a **user**,
I want **changes in control or risk status to be reflected instantly on my dashboard**,
So that **I always have up-to-date information for decision-making**.

**Acceptance Criteria:**
**Given** a BPO updates the status of a control,
**When** the update is saved,
**Then** the relevant metrics and displays on the Executive's dashboard update within one minute without requiring a page refresh.
**And** the changes are reflected in any open list views for other users.

**Prerequisites:** Epic 1 (Core Data CRUD), Epic 4.1 (Dashboards).
**Technical Notes:** Implement Supabase Realtime for instant updates (e.g., using WebSockets). Frontend subscribes to relevant database changes.

### Story 4.3: Develop Streamlined Control Assessment Workflow for BPOs
As a **Business Process Owner (BPO)**,
I want **a simple and intuitive interface to assess assigned controls**,
So that **I can efficiently complete my compliance tasks**.

**Acceptance Criteria:**
**Given** I am logged in as a BPO,
**When** I access my dashboard,
**Then** I see a list of controls assigned to me that require assessment.
**And** I can select a control, choose an assessment status (e.g., "Effective", "Ineffective", "Needs Improvement"), and add comments in under 5 clicks.
**And** the assessment action is logged to the immutable audit trail (FR-8).

**Prerequisites:** Epic 2 (BPO role), Epic 4.1 (BPO Dashboard), Epic 3.4 (Audit Trail).
**Technical Notes:** Dedicated frontend forms/modals for assessments. Backend endpoints to process assessments and trigger audit logging.

---

## Epic 5: Advanced Compliance Mapping & Reporting

**Goal:** Enable the central compliance mapping feature and provide basic reporting.

### Story 5.1: Implement Many-to-Many Compliance Mapping UI
As an **Admin**,
I want **to link internal controls to specific requirements within various regulatory frameworks**,
So that **I can establish a comprehensive mapping for gap analysis**.

**Acceptance Criteria:**
**Given** I am managing a control and a regulatory framework (FR-2),
**When** I access the mapping interface,
**Then** I can select multiple regulatory requirements to associate with a single control.
**And** I can select multiple controls to associate with a single regulatory requirement.
**And** the mapping is visually clear and easy to manage (e.g., using a multi-select component or dual-list box).

**Prerequisites:** Epic 1 (Core Data CRUD for controls/regulatory frameworks), Epic 2 (Admin role).
**Technical Notes:** New junction table in the database to manage the many-to-many relationship (`controls_regulatory_requirements`). Frontend UI components for intuitive selection.

### Story 5.2: Develop Gap Analysis Report Generation
As an **Admin or Executive**,
I want **to generate a report showing compliance gaps for a selected regulatory framework**,
So that **I can understand areas of non-compliance and prioritize remediation efforts**.

**Acceptance Criteria:**
**Given** controls are mapped to a regulatory framework (Story 5.1),
**When** I select a regulatory framework and request a gap analysis report,
**Then** the system identifies any regulatory requirements that have no associated controls.
**And** the report clearly lists these "gap" requirements.
**And** the report is exportable (e.g., basic browser print-to-PDF).

**Prerequisites:** Story 5.1.
**Technical Notes:** Backend service to query the database for unmapped regulatory requirements. Frontend to display and format the report.

---

## FR Coverage Matrix

-   **FR-1: Role-Based Access Control** → Epic 2, Story 2.1, Story 2.2
-   **FR-2: Core Data CRUD** → Epic 1, Story 1.2, Story 1.3, Story 1.4
-   **FR-3: Compliance Mapping** → Epic 5, Story 5.1, Story 5.2
-   **FR-4: AI-Assisted Document Analysis** → Epic 3, Story 3.1, Story 3.2
-   **FR-5: Human-in-the-Loop (HITL) Validation** → Epic 3, Story 3.3
-   **FR-6: Role-Specific Dashboards** → Epic 4, Story 4.1
-   **FR-7: Real-Time Status Updates** → Epic 4, Story 4.2
-   **FR-8: Immutable Audit Trail** → Epic 3, Story 3.4
-   **FR-9: Streamlined Control Assessment** → Epic 4, Story 4.3

---

## Summary

The complete epic and story breakdown for ibe160 has been created. The project is structured into 5 epics, each delivering user value incrementally. All 9 functional requirements from the PRD are covered by one or more stories. The stories include detailed acceptance criteria, prerequisites, and technical notes, making them actionable for development.

---

_For implementation: Use the `create-story` workflow to generate individual story implementation plans from this epic breakdown._

_This document will be updated after UX Design and Architecture workflows to incorporate interaction details and technical decisions._