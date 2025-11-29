# ibe160 - Product Requirements Document

## TL;DR
*   **What:** We are building a SaaS tool to replace compliance spreadsheets.
*   **How:** An "AI Legal Specialist" will automatically find compliance gaps in documents.
*   **Goal:** Reduce audit preparation time and provide real-time risk visibility.

**Author:** BIP
**Date:** November 23, 2025
**Version:** 1.0

---

## Executive Summary

The Risk Control Matrix project will create a centralized, dynamic SaaS platform to replace manual, spreadsheet-based methods for managing internal controls and business risks. Its core purpose is to provide real-time visibility into a company's compliance posture by systematically mapping internal controls to external laws and regulations. By leveraging AI-assisted workflows, the platform will empower compliance officers, business process owners, and executives to perform gap analyses, simplify audits, and proactively manage risk.

### What Makes This Special

The "wow" moment, the core magic of this product, is when a user gets a custom-made, clear, and immediate picture of which legal requirements are not fulfilled by their existing governing documents or procedures. The application will act as a dedicated legal specialist, instantly highlighting compliance gaps and translating complex regulatory language into actionable insights. This moves beyond simple risk management to provide proactive, AI-driven legal intelligence.

---

## Project Classification

**Technical Type:** SaaS B2B
**Domain:** GRC (Governance, Risk, and Compliance)
**Complexity:** High

This is a greenfield B2B SaaS platform operating in the high-complexity Governance, Risk, and Compliance (GRC) domain.

### Domain Context

The GRC domain is inherently complex, requiring the system to:
- Interpret and map multiple external laws and regulations.
- Manage a detailed and auditable trail of internal controls and assessments.
- Provide tailored views and permissions for distinct corporate roles, from general employees to the Board of Directors.
- Handle sensitive data related to corporate risk and compliance posture.
The AI's role as a "legal specialist" is critical to navigating this complexity and providing clear, actionable guidance.

---

## Success Criteria

The primary measure of success is the tangible impact on the business's compliance and audit cycles. Winning means transforming a slow, manual, and uncertain process into a fast, automated, and trustworthy one.

### Business Metrics

Success will be measured against four key pillars:

1.  **Business Objective:** Reduce person-hours spent on audit preparation by 80%.
2.  **System Adoption:** Achieve 95% management of all active business controls within the platform 4 months post-launch, enabling the full retirement of the legacy spreadsheet system.
3.  **Auditability & Trust:** The platform's automated audit trail is accepted as the single source of truth during compliance audits, eliminating the need for manual data gathering and reconciliation.
4.  **AI Effectiveness:** The AI-driven gap analysis identifies compliance gaps with over 90% accuracy, as validated by a compliance officer, providing an actionable report that serves as the starting point for remediation.

---

## Product Scope

The product will be developed across three horizons: an initial Minimum Viable Product (MVP) to solve the core problem, a Growth phase to make it competitive, and a long-term Vision to lead the market.

### MVP - Minimum Viable Product

The MVP is focused on delivering the core "AI legal specialist" value proposition. It must provide a functional, trustworthy tool that is a clear improvement over manual spreadsheets.

-   **Core Data Management:** Full CRUD (Create, Read, Update, Delete) capabilities for the central risk matrix table, the risk register, and the control library.
-   **Regulatory Mapping:** The essential feature allowing users to link internal controls to specific external regulations.
-   **Simple Role-Based Access:** Foundational roles for Admin, Business Process Owner (BPO), Executive, and General User to ensure data security.
-   **Basic Dashboard:** A high-level dashboard providing an at-a-glance overview of the organization's risk posture.
-   **AI-Assisted Workflow:** The initial implementation of the AI engine to analyze uploaded regulatory documents and suggest relevant risks and controls.

### Growth Features (Post-MVP)

Following a successful MVP launch, these features will be prioritized to enhance user efficiency, deepen the product's value, and improve its competitive standing.

-   **Automated Notifications:** Proactive email reminders and in-app alerts for Business Process Owners when control assessments are due or overdue.
-   **Granular Permissions (RBAC):** Evolve from simple roles to a granular, position-based access control system to more accurately reflect company structures.
-   **Automated Data Import:** A tool to seamlessly import existing risk and control data from spreadsheets (e.g., CSV, Excel), significantly easing customer onboarding.
-   **Advanced PDF Reporting:** Move beyond simple browser printing to generate professionally formatted, customizable PDF reports suitable for executive and board-level presentation.

### Vision (Future)

The long-term vision is to evolve the product from an "AI-assisted" tool into a fully autonomous compliance partner.

-   **Proactive AI Agent:** The AI will transform into a proactive agent that constantly monitors public feeds for updates to legal and regulatory frameworks.
-   **Autonomous Suggestions:** Instead of waiting for a user to upload a document, the AI will automatically identify relevant changes and proactively suggest updates or additions to the company's internal controls, complete with rationale and risk analysis.
-   **Predictive Analytics:** The platform will analyze trends in compliance data to predict future risk areas and recommend preventative measures.
-   **Deep Enterprise Integration:** Seamlessly connect with other core business systems (e.g., ERP, HRIS, CRM) to automatically infer business processes and risks, providing a truly holistic view of compliance.

### Logical Progression

The three scope horizons are strategically dependent. The **MVP** establishes the foundational data model and the core AI workflow. The **Growth** phase builds upon this by enhancing data quality (via imports and granular RBAC) and creating the necessary communication channels (notifications). This mature ecosystem is the critical prerequisite for realizing the **Vision**, as an autonomous AI requires a high-integrity data environment and established pathways to deliver its proactive insights. The success of the entire roadmap hinges on the initial AI workflow in the MVP being effective and trustworthy.

### Core Assumption & De-risking Strategy

The central assumption for this entire product is that **an AI can be a trusted and reliable legal specialist for compliance analysis.** The three-phase roadmap is designed to systematically de-risk this assumption:

1.  **MVP (Test the Assumption):** The initial AI workflow will prove the technical feasibility and baseline accuracy in a controlled, human-supervised environment.
2.  **Growth (Build Trust in the Assumption):** By improving data quality, adding feedback loops, and demonstrating consistent value, we will build user trust in the AI's recommendations.
3.  **Vision (Capitalize on the Validated Assumption):** Once the AI is proven and trusted, we can grant it autonomy to act as a proactive compliance partner.

---

## Domain-Specific Requirements

Operating in the GRC domain imposes a set of strict, non-negotiable requirements that influence the entire product architecture and feature set.

-   **Auditability is Paramount:** Every significant action—creating, updating, or assessing a control or risk—must be logged in an immutable audit trail. This log must capture the "who, what, and when" to be considered a single source of truth during audits.
-   **Data Security and Confidentiality:** The system will house sensitive data about a company's risks and compliance posture. Therefore, standard industry practices for data security, such as encryption of data at rest and in transit, are mandatory.
-   **Regulatory Flexibility:** The system cannot be hard-coded for a single regulation (e.g., GDPR). It must be architected to support multiple, user-defined regulatory frameworks, allowing users to upload and map controls against various legal standards (e.g., SOX, ISO 27001, etc.).
-   **Human-in-the-Loop Validation:** Given the high-stakes nature of legal compliance, the AI cannot be a "black box." Every suggestion made by the AI (e.g., a potential risk, a recommended control) must be presented to a qualified user (like a Compliance Officer) for validation and approval before it becomes an active part of the system. This builds trust and ensures accountability.
-   **Reliability over Speed:** In cases of ambiguity, the system must favor accuracy and reliability over processing speed. An inaccurate gap analysis is more dangerous than a slow one. This principle must guide the design of the AI workflows.

This section shapes all functional and non-functional requirements below.

---

## Innovation & Novel Patterns

The core innovation is the creation of a **Specialist AI Persona**. Instead of using a generic AI, we are building a bespoke "AI Legal Specialist." This involves fine-tuned prompt engineering that enables the AI to analyze compliance documents with a specific, expert persona. This approach challenges the assumption that GRC software is merely a passive database and transforms it into an active, intelligent partner for the user.

This pattern combines two concepts:
1.  **Domain-Specific Language Model Application:** Applying an LLM to the highly specialized domain of legal and regulatory compliance.
2.  **Persona-Driven Interaction:** The AI is not a neutral tool; it is designed to interact and provide recommendations as a legal specialist would, making its advice more contextual and actionable.

### Validation Approach

The innovation will be validated through a combination of quantitative metrics and a qualitative, human-in-the-loop workflow.

1.  **Primary Validation Metric:** The success of this innovation is directly tied to the "AI Effectiveness" metric defined in the Success Criteria: **"The AI-driven gap analysis identifies compliance gaps with over 90% accuracy, as validated by a compliance officer."** If the human expert consistently agrees with the AI's output, the specialist persona is considered effective.
2.  **Workflow Validation:** The "Human-in-the-Loop" requirement (from Domain-Specific Requirements) is the core validation mechanism. Every AI suggestion is subject to review by a qualified user. This process not only prevents errors but also allows us to gather data on the AI's performance, which is crucial for future improvements and building user trust.
3.  **Fallback Mechanism:** Should the AI's suggestions prove unreliable, the system's value is not entirely lost. The platform's core functionality as a structured database for manually managing risks and controls serves as a robust fallback. This ensures that the product remains useful even if the primary innovation requires further iteration.

---

## SaaS B2B Specific Requirements

As a multi-customer SaaS platform, the architecture must be designed to support the needs of distinct business clients securely and efficiently.

### Multi-Tenancy Architecture

The system will be designed as a multi-tenant application where data from one customer (tenant) is logically isolated from all others. While all customers will share the same application and database infrastructure, data will be partitioned using a unique `tenant_id` on all relevant tables. Row-Level Security (RLS) policies in the database will enforce this separation, ensuring that a user from one company can under no circumstances access data belonging to another. This provides a cost-effective and scalable model for the service.

### Permissions & Roles

The permission model for the MVP will be based on a simple, role-based access control (RBAC) system defined for each tenant. The following roles are mandatory:

-   **Admin:** Has full CRUD (Create, Read, Update, Delete) access over all data within their tenant, including user management and system settings.
-   **Business Process Owner (BPO):** Can view all data but only has write access to assessing the specific controls they are assigned as the owner.
-   **Executive:** Has read-only access to all data and dashboards within their tenant, but no write permissions.
-   **General User:** Has read-only access to view final, approved processes, risks, and controls. Cannot view draft or sensitive assessment data.

This initial model will be expanded in the Growth phase to support more granular, position-based permissions.

### Future Considerations

While out of scope for the MVP, the architecture should not preclude the future implementation of:
-   **Subscription Tiers:** A billing and subscription management system to support different feature tiers (e.g., Free, Pro, Enterprise).
-   **Third-Party Integrations:** APIs and webhooks to allow for future integration with other enterprise systems as defined in the product vision.

---

## User Experience Principles

The user experience must inspire confidence, clarity, and trust. Given the serious nature of the GRC domain, the application is a tool for professionals, and its design must reflect that. The overall vibe should be **authoritative, minimalist, and data-first.**

-   **Visual Personality:** The UI should be clean, structured, and professional. It will prioritize information density and clarity over decorative elements. A high-contrast, typography-focused design using a modern, minimalist framework (like the chosen Shadcn UI) will ensure the focus remains on the data.
-   **Feel:** Using the application should feel like working with a calm, competent, and expert partner. It should be efficient and clear, never playful or distracting. The goal is to reduce cognitive load, not add to it.
-   **Reinforcing the "Magic":** The UI must be designed to build trust in the "AI Legal Specialist." AI-generated suggestions should be visually distinct from human-verified data and always be presented with a clear explanation of their reasoning (e.g., "This gap was identified based on clause 4.2.a of the regulation.").

### Key Interactions

-   **Dashboard-Centric Workflow:** For each role, the dashboard is the primary entry point. It must immediately present the most critical information and required actions for that user (e.g., pending assessments for a BPO, high-level risk posture for an Executive).
-   **Drill-Down, Don't Drown:** Users must be able to click on any high-level data point (a chart, a risk score, a summary number) and seamlessly drill down into the underlying, granular details. The information hierarchy should be clear and intuitive.
-   **Human-in-the-Loop:** The interaction for validating AI suggestions is a critical flow. It must be a deliberate, clear loop:
    1.  AI *suggests* and *explains*.
    2.  User *reviews* the suggestion and explanation.
    3.  User explicitly *approves* or *rejects* the suggestion. This action should be logged in the audit trail.

---

## Functional Requirements

The following requirements are derived from the scope, domain needs, and UX principles defined above. They are organized by user-facing capability.

### 1. User & Access Management
This capability ensures that users can be managed and can only access data and features appropriate for their role.

-   **FR-1: Role-Based Access Control:** The system must support four distinct user roles within each tenant: Admin, Business Process Owner (BPO), Executive, and General User.
    -   *User Value:* Ensures data security and simplifies the user experience by only showing relevant actions.
    -   *Acceptance Criteria:* A user logged in with the "General User" role cannot see any "Edit" or "Create" buttons. An "Admin" user can access a user management panel.

### 2. Compliance Data Management
This capability covers the core creation and management of the GRC data that forms the foundation of the system.

-   **FR-2: Core Data CRUD:** Authorized users (primarily Admins) must be able to Create, Read, Update, and Delete the core data entities: Business Processes, Risks, Controls, and Regulatory Frameworks.
    -   *User Value:* Provides a centralized, single source of truth for all compliance data, replacing disparate spreadsheets.
    -   *Acceptance Criteria:* An Admin can successfully create a new control, add a description, edit that description, and then delete the control. When creating a control, an 'owner' (a user with the BPO role) must be assigned; the system will not allow the creation of an unassigned control.
-   **FR-3: Compliance Mapping:** The system must allow many-to-many mapping between controls and the specific requirements within regulatory frameworks.
    -   *User Value:* Enables the core gap analysis function by creating explicit links between internal actions and external rules.
    -   *Acceptance Criteria:* A user can link a single internal control to three different requirements across two different regulatory frameworks.

### 3. AI-Powered Gap Analysis
This capability is the "magic" of the product, where the AI Legal Specialist actively assists users in their compliance tasks.

-   **FR-4: AI-Assisted Document Analysis:** An Admin must be able to upload a regulatory document (e.g., in PDF or text format). The system will use the AI to parse the document and present a list of suggested risks and controls based on its content.
    -   *User Value:* Drastically reduces the manual effort required to understand and act on new regulations. Delivers the core "wow"
    -   *Acceptance Criteria:* Given a test regulatory document with 5 known, actionable requirements, the AI correctly identifies and suggests relevant controls for at least 4 of them. Conversely, given a document with no actionable requirements (e.g., a marketing page), the AI correctly returns zero suggestions.
-   **FR-5: Human-in-the-Loop (HITL) Validation:** All AI-generated suggestions must be presented to a qualified user for explicit approval or rejection before they become active data in the system.
    -   *User Value:* Builds trust and ensures accountability, leveraging AI's speed while retaining human expertise and oversight.
    -   *Domain Constraint:* This is a mandatory requirement for operating in the high-stakes GRC domain.
    -   *Acceptance Criteria:* An AI-suggested control is visually marked as "unverified" and has "Approve" and "Reject" buttons. Clicking "Approve" makes the control a permanent, visible part of the control library.

### 4. Risk & Compliance Monitoring
This capability provides real-time visibility into the organization's compliance posture for different audiences.

-   **FR-6: Role-Specific Dashboards:** The application must present a tailored dashboard experience for each user role upon login.
    -   *User Value:* Immediately provides the most relevant information to each user, saving time and improving focus.
    -   *Acceptance Criteria:* An Executive sees a high-level chart of risk distribution. A BPO sees a task list of their pending control assessments.
-   **FR-7: Real-Time Status Updates:** Changes in the status of a control or risk must be reflected on all relevant dashboards in near real-time.
    -   *User Value:* Provides trustworthy, up-to-date information for decision-making.
    -   *Acceptance Criteria:* When a BPO marks a control as "Ineffective," the overall risk score on the Executive's dashboard is updated within one minute without requiring a page refresh.

### 5. Audit & History
This capability ensures that a complete and trustworthy history of all compliance activities is maintained.

-   **FR-8: Immutable Audit Trail:** All actions that create, modify, or delete critical compliance data (including risks, controls, and assessments) must be recorded in an immutable audit log.
    -   *User Value:* Radically simplifies audit preparation and provides a bulletproof record of compliance activities.
    -   *Domain Constraint:* This is a fundamental requirement for any GRC platform.
    -   *Acceptance Criteria:* When a user edits the description of a control, a new log entry is created that includes the user's ID, the timestamp, the name of the control, the previous description, and the new description.

### 6. Control Assessment
This capability, identified during stakeholder analysis, defines the critical workflow for BPOs.

-   **FR-9: Streamlined Control Assessment:** The system must provide a simple, intuitive interface for a BPO to assess an assigned control. This workflow will be the primary interaction for all BPO users.
    -   *User Value:* Ensures BPOs can complete their compliance tasks with minimal friction, encouraging adoption and timely completion.
    -   *Acceptance Criteria:* From their dashboard, a BPO can open, assess (e.g., select 'Effective' or 'Ineffective'), add a comment, and submit a control assessment in under 5 clicks.

---

## Non-Functional Requirements

These requirements define the quality attributes of the system, ensuring it is robust, secure, and efficient.

### Performance

A responsive and efficient user experience is critical for professional users who value their time.
-   **Why it matters:** A slow or laggy interface will frustrate users and hinder adoption, especially for BPOs who need to complete tasks quickly.
-   **Criteria:**
    -   Core interactive pages (dashboards, lists, reports) must achieve a Largest Contentful Paint (LCP) of less than 2.5 seconds to meet Google's Core Web Vitals standard for a "Good" user experience.
    -   Asynchronous operations, such as AI analysis, must not block the UI. They must provide immediate feedback to the user (e.g., a loading indicator or progress bar) and notify the user upon completion.

### Security

The system will store highly sensitive data regarding a company's internal risks and compliance posture. Security is therefore non-negotiable.
-   **Why it matters:** A security breach would be catastrophic to customer trust and could have severe financial and legal repercussions.
-   **Criteria:**
    -   All data must be encrypted at rest (in the database) and in transit (using TLS 1.2+).
    -   The application must be developed following OWASP Top 10 guidelines to protect against common vulnerabilities.
    -   All third-party dependencies must be scanned for known vulnerabilities before deployment.
    -   The system must pass a third-party security audit before its first commercial release.

### Scalability

As a SaaS product, the system must be able to grow with its customers, both in the number of users and the volume of compliance data.
-   **Why it matters:** The architecture must support growth without requiring a costly redesign.
-   **Criteria:**
    -   The system must be architected to support a baseline of 100 concurrent users per tenant for the MVP.
    -   Database queries must remain performant, even on tables containing over 1 million rows (e.g., controls, risks, audit logs). Key queries should execute in under 500ms.

### Accessibility

The application should be usable by all employees within a customer's organization.
-   **Why it matters:** Ensures the tool is inclusive and compliant with potential corporate procurement policies that mandate accessibility.
-   **Criteria:** The application should strive for Web Content Accessibility Guidelines (WCAG) 2.1 Level AA compliance. For the MVP, this specifically includes high-contrast color choices, full keyboard navigation for all interactive elements, and proper labeling for screen readers.

---

## Implementation Planning

### Epic Breakdown

The functional requirements have been decomposed into 5 epics, each representing a major phase of development that delivers incremental value. The full breakdown of epics into user stories can be found in the `epics.md` document.

-   **Epic 1: Foundational Setup & Core Compliance Data Model:** Establishes the project's technical foundation and creates the core data structures for managing compliance information.
-   **Epic 2: User Identity & Access Management (IAM):** Enables secure user access and enforces role-based permissions for Admins, BPOs, Executives, and General Users.
-   **Epic 3: AI-Powered Gap Analysis & Auditing:** Delivers the core "AI Legal Specialist" by enabling document analysis, human-in-the-loop validation, and a complete audit trail.
-   **Epic 4: Real-Time Risk Monitoring & Assessment:** Provides real-time dashboards tailored to user roles and the primary workflow for Business Process Owners to assess controls.
-   **Epic 5: Advanced Compliance Mapping & Reporting:** Enables the central many-to-many compliance mapping feature, allowing controls to be linked to regulatory requirements.

**Next Step:** With the PRD and initial epic breakdown complete, the next steps involve detailed technical design and user experience planning.


---

## References

- Product Brief: {project-root}/docs/product-brief-ibe160-2025-11-17.md
- Research:
  - {project-root}/docs/research-technical-2025-11-17-tech-stack-analysis.md
  - {project-root}/docs/research-technical-2025-11-17 Backend Deployment Strategy.md
  - {project-root}/docs/research-technical-2025-11-16 LLM Orchestration.md
  - {project-root}/docs/research-2025-11-08 buy-vs-build-analysis.md

---

## Next Steps

1. **Epic & Story Breakdown** - Run: `workflow epics-stories`
2. **UX Design** (if UI) - Run: `workflow ux-design`
3. **Architecture** - Run: `workflow create-architecture`

---

_This PRD captures the essence of ibe160 - The application will act as a dedicated legal specialist, instantly highlighting compliance gaps and translating complex regulatory language into actionable insights._

_Created through collaborative discovery between BIP and AI facilitator._
