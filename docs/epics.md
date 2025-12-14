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
I want **to initialize the project from the chosen `vintasoftware/nextjs-fastapi-template`**,
So that **we have a stable and consistent foundation for building the application, aligned with architectural decisions**.

**Acceptance Criteria:**
**Given** the `vintasoftware/nextjs-fastapi-template` is selected,
**When** the project initialization process is complete,
**Then** a new repository is created from the template.
**And** all dependencies are installed using `uv` and `pnpm`.
**And** environment variables (`.env`) are configured for Supabase, OpenAI, and SendGrid.
**And** the application runs successfully via `docker compose up`.
**And** the `pgvector` extension is enabled in the Supabase database.

**Prerequisites:** None
**Technical Notes:** This story sets up the entire repository and CI/CD pipeline foundation. It should include basic linting, formatting, and environment variable setup, as well as the initial database setup.

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

### Story 2.3: Admin User Creation & Role Assignment
As an **Admin**,
I want **to create new users and assign them specific roles (Admin, BPO, Executive, General User)**,
So that **I can manually onboard users and ensure they have the correct permissions immediately**.

**Acceptance Criteria:**
**Given** I am logged in as an Admin,
**When** I access the "Users" management page,
**Then** I see a "Create User" button.
**And** clicking it opens a form to enter email, password (optional/temporary), and select a role.
**And** submitting the form creates the user in Supabase Auth and the `users` table with the selected role.
**And** the new user appears in the user list.

**Prerequisites:** Story 2.2.
**Technical Notes:** Use Supabase Admin API (`service_role` key) in the backend to create users without requiring email verification flow if preferred, or trigger standard invite. Ensure `public.users` table is synced.

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
As a **Compliance Officer (CO)**,
I want **to use the two-stage "AI Review Mode" to efficiently triage AI suggestions and route them for final BPO approval**,
So that **I can act as an effective gatekeeper while ensuring business-level accountability**.

**Acceptance Criteria:**
**Given** a document has been analyzed by the AI,
**When** I enter "AI Review Mode",
**Then** I see a two-panel layout with a list of suggestions on the left and details on the right.
**And** I can use "Accept" to promote a suggestion to the "Pending Review" queue for the designated BPO.
**And** promoting a suggestion routes it to the BPO's dashboard and sends a notification.
**And** the original `source_reference` from the AI analysis is permanently attached to the item for the BPO to see.
**And** dismissing a suggestion removes it from my triage view.

**Prerequisites:** Story 3.2.
**Technical Notes:** Frontend development for the "AI Review Mode" interface with two-panel layout. Backend endpoints to handle suggestion promotion and routing to BPO queues. Supabase Realtime for notifications.

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
I want **an "Action-Oriented Hub" dashboard tailored to my role upon login**,
So that **I immediately see the most critical information and actions, and can easily initiate core workflows**.

**Acceptance Criteria:**
**Given** I am logged in with a specific role (Admin, BPO, Executive, General User),
**When** I land on the dashboard,
**Then** the content and layout of the dashboard are customized to my role with a grid of modular cards.
**And** the dashboard features a prominent "Analyze New Document" button for COs.
**And** a BPO sees a "Pending Reviews" card with a count of items awaiting action.
**And** the dashboard loads quickly (LCP < 2.5s).

**Prerequisites:** Epic 2 (RBAC), Epic 1 (Core Data CRUD for metrics).
**Technical Notes:** Frontend conditional rendering based on user role. Utilize Shadcn/UI for modular cards and Recharts for data visualization. Backend endpoints providing role-specific data feeds.

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
I want **to act on items in my "Pending Review" queue via a dedicated review screen**,
So that **I can make the final, accountable decision on new controls and risks**.

**Acceptance Criteria:**
**Given** a CO has routed an item to my "Pending Review" queue (from Story 3.3),
**When** I access my dashboard and click on the "Pending Reviews" card,
**Then** I see a list of items awaiting my final decision.
**And** selecting an item takes me to a detailed review screen with editable AI-suggested data.
**And** I can "Approve" (making it Active), "Edit" (with changes tracked in a "Change Log"), or "Discard" (moving it to a temporary archive).
**And** I must categorize the "Residual Risk" (low, medium, high) before approval.
**And** the assessment action, including edits and final decision, is logged to the immutable audit trail (FR-8).

**Prerequisites:** Epic 2 (BPO role), Epic 4.1 (BPO Dashboard), Epic 3.4 (Audit Trail), Story 3.3.
**Technical Notes:** Dedicated frontend review screen leveraging Shadcn/UI. Backend endpoints to process assessments, manage change logs, and trigger audit logging.

### Story 4.4: Dashboard UX Enhancements
As a **user**,
I want **my user icon in the dashboard to display my name instead of a generic "U"**,
So that **the interface feels personalized and I can verify my identity at a glance**.

**Acceptance Criteria:**
**Given** I am logged in,
**When** I view the dashboard header/sidebar,
**Then** the user avatar displays my initials (e.g., "JD" for John Doe) or my full name if space permits.
**And** hovering over the icon shows my full name and role (e.g., "John Doe (Admin)").
**And** this persists across all dashboard pages.

**Prerequisites:** Epic 4.1.
**Technical Notes:** Ensure the `users` table has `first_name` / `last_name` or `full_name` fields, or derive from email if necessary (though name is preferred). Update the `UserNav` or `Avatar` component.

### Story 4.6: Overview Page
As a **user**,
I want **to view all accepted risks, controls, and business processes in a unified hierarchical overview page**,
So that **I can see the complete compliance framework in one place with processes as parent items linking to their associated controls and risks**.

**Acceptance Criteria:**
**Given** risks, controls, and processes have been accepted from the AI Review workflow,
**When** I navigate to the Overview page (`/dashboard/overview`),
**Then** I see all accepted items displayed in an expandable tree structure with processes as parent nodes.
**And** each process expands to show its associated controls and risks as child nodes.
**And** I can toggle between tree view and tabbed views (Processes | Controls | Risks).
**And** as an Admin, I can edit or delete items inline using modal dialogs without leaving the page.
**And** as a non-Admin user, I have read-only access to view all items.
**And** the Dashboard card titled "Overview" shows the total count of accepted items (risks + controls + processes) and links to this page.

**Prerequisites:** Epic 3 (AI Review workflow), Epic 4.1 (Dashboard cards).
**Technical Notes:** Replace the "System Health" card in Admin dashboard with "Overview" card. Implement `/dashboard/overview` page with tree component and modal edit/delete forms. All roles can access the page (read), but only Admin can edit/delete. Update dashboard_service.py to calculate metric including processes count.

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

### Story 5.3: Regulatory Frameworks Enhancement
As an **Admin**,
I want **uploaded regulatory documents to be automatically classified as Main Laws or Regulations by AI, with Regulations linked to parent Laws in a hierarchical structure**,
So that **I can maintain an organized regulatory framework that reflects the actual legal structure (laws → regulations)**.

**Acceptance Criteria:**
**Given** I upload a regulatory document and click "Process Now",
**When** the AI analyzes the document,
**Then** the AI automatically determines if the document is a Main Law or a Regulation.
**And** if it's a Regulation, the AI identifies and links it to the appropriate parent Law (creating the Law if it doesn't exist).
**And** the Regulatory Frameworks page (`/dashboard/regulatory-frameworks`) displays a hierarchical tree view showing Laws as parent nodes with their associated Regulations as children.
**And** each framework item shows its linked source document(s).
**And** one document can only be linked to one law or regulation (not multiple).
**And** users can manually override the AI classification if needed (future enhancement - note in Dev Notes).

**Prerequisites:** Epic 3 (Document upload and AI analysis).
**Technical Notes:** Modify `regulatory_frameworks` table to include `parent_id` (self-referencing foreign key) and `type` field (enum: 'law' or 'regulation'). Update AI prompt in document processing to classify document type and identify parent Law. Enhance `/dashboard/regulatory-frameworks` page with tree component. Add document_id foreign key to link frameworks to source documents. This uses hierarchical single-table design (Option B from planning discussion).

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