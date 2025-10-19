## Case Title
Risk Control Matrix

## Background
Many companies, especially as they scale, struggle to manage their internal controls and identify business risks effectively. They often rely on static spreadsheets and manual processes, which are error-prone, difficult to maintain, and provide no real-time visibility into their compliance posture. A significant challenge is ensuring that internal policies and controls comprehensively cover all requirements from external laws and regulations. Without a systematic way to map these, it is difficult to perform a gap analysis, leaving the organization vulnerable to compliance violations. This makes it challenging to prepare for audits and adapt to regulatory changes.

## Purpose
The purpose of the Risk Control Matrix is to provide a centralized, dynamic platform for companies to document, assess, and monitor their internal controls and associated risks. A key feature will be the ability to map internal controls and policies to external laws and regulations, enabling the system to perform a gap analysis and highlight areas where governance is missing. It will replace manual spreadsheet-based methods, improve accuracy, and offer real-time insights to simplify compliance and audit processes.

## Target Users
- **Compliance Officers / Managers:** They are responsible for the overall compliance framework, defining controls, and reporting to leadership.
- **Internal Auditors:** They use the application to test controls, review evidence, and track remediation efforts.
- **Business Process Owners:** These are managers or team leads who are responsible for implementing and maintaining controls within their specific departments (e.g., Head of IT, Head of Finance).
- **Executives / Senior Leadership:** They need high-level dashboard views to understand the overall risk posture of the organization.
- **Board of Directors:** Reviews and approves the final risk matrix report.

### Must Have (MVP)
- **Control Library:** A centralized place to define and manage a library of all internal controls. Each control should have properties like a name, description, owner, and frequency (e.g., annual, quarterly).
- **Risk Register:** A place to document and categorize all business risks. Each risk should be linkable to one or more controls that mitigate it.
- **Assessment & Testing:** The ability for auditors or owners to perform assessments on controls, record the results (e.g., "Effective," "Ineffective"), and attach evidence.
- **Dashboard & Reporting:** A visual dashboard showing the overall risk posture, control effectiveness, and status of assessments. Ability to generate PDF reports for leadership and the Board of Directors.
- **Regulatory Framework Mapping:** Ability to map controls to specific requirements from different regulations (e.g., SOX, GDPR, ISO 27001).
- **Gap Analysis:** A feature to analyze the mappings between internal policies/controls and external regulations to automatically identify and report on which regulations are not being met.

### Nice to Have (Optional Extensions)
- **Automated Notifications:** Automatic email reminders to control owners when tasks are due or overdue.

## Data Requirements

- **Business Processes:** `id`, `name`, `description`, `owner_position_id`.
- **Users:** `id`, `name`, `email`, `password`, `position_id` (linking them to their official role).
- **Positions:** `id`, `title` (e.g., 'Chief Financial Officer', 'IT Manager'), `department`. This represents the organizational chart.
- **Rules & Regulations:** `id`, `name` (e.g., 'GDPR', 'SOX Section 302'), `description`, `source_document_url`.
- **Internal Policies:** `id`, `title` (e.g., 'IT Security Policy'), `version`, `content_or_link`.
- **Controls:** `id`, `name`, `description`, `business_process_id`, `owner_position_id` (the role responsible for the control).
- **Risks:** `id`, `name`, `description`, `severity`.
- **Assessments:** `id`, `control_id`, `auditor_position_id`, `status`, `notes`.
- **Link Tables:** To connect entities (e.g., linking Controls to Risks, Regulations, and Policies).

## User Stories

1. As a **Compliance Officer**, I want to **map a single control to multiple regulations** so that I can efficiently manage compliance across different legal frameworks.
2. As an **Internal Auditor**, I want to **view all controls and their assessment history for a specific business process** so that I can prepare for an upcoming audit.
3. As a **Business Process Owner**, I want to **see a clear list of my controls that have been assessed as 'Ineffective' on my dashboard** so that I can take immediate corrective action.
4. As an **Executive**, I want to **view a dashboard with the top 10 unmitigated risks** so that I can understand the company's current risk exposure at a glance.

## Technical Constraints

- **Must support user authentication with Role-Based Access Control (RBAC):** Users should only be able to see and do what their specific position requires.
- **Must be a web-based application, responsive for modern browsers:** Ensures accessibility from any company computer without installation.
- **Must have an audit trail:** All changes to critical data must be logged to track who did what, and when.
- **Data must be encrypted at rest and in transit:** A standard security requirement for handling sensitive corporate data.

## Success Criteria

- **Criterion 1: End-to-End Audit Workflow:** A Compliance Officer can successfully create a new control, link it to a regulation, have an Auditor assess it, and an Executive can view the result in a report.
- **Criterion 2: Role-Based Access is Enforced:** A user logged in with a "Business Process Owner" position cannot access or perform actions reserved for an "Internal Auditor".
- **Criterion 3: Audit Trail Integrity:** All create, update, and delete actions on controls and assessments are successfully logged in the audit trail with the correct user and timestamp.
- **Criterion 4: Report Generation:** The system can generate a PDF report of the current risk matrix that is clear and readable for the Board of Directors.
- **Criterion 5: Interactive Gap Analysis:** For a selected regulation, the system generates a report of all requirements not mapped to an internal control. A user can then initiate the creation of a new, pre-linked control directly from an item in that report.