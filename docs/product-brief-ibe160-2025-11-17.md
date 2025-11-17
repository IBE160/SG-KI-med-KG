# Product Brief: Risk Control Matrix

**Date:** Monday, November 17, 2025
**Author:** BIP
**Context:** Enterprise SaaS Application

---

## Executive Summary

The Risk Control Matrix is a centralized, dynamic SaaS platform designed to replace manual, spreadsheet-based methods for managing internal controls and business risks. Its core purpose is to provide real-time visibility into a company's compliance posture by systematically mapping internal controls to external laws and regulations. By leveraging AI-assisted workflows, the platform will empower compliance officers, business process owners, and executives to perform gap analyses, simplify audits, and proactively manage risk. The initial MVP will focus on delivering a highly customized and intuitive experience for core risk management and compliance tasks, with a long-term vision for commercialization.

---

## Core Vision

### Problem Statement

Companies, particularly as they scale, struggle to manage their internal controls and identify business risks effectively. They rely on static, error-prone spreadsheets that offer no real-time visibility into their compliance posture. A significant challenge is the inability to systematically map internal policies to external regulations, making it difficult to perform gap analyses and leaving the organization vulnerable to compliance violations and unprepared for audits.

### Problem Impact

This reliance on manual processes leads to:
- Increased risk of compliance violations and associated fines.
- Inefficient and time-consuming audit preparation.
- Lack of real-time visibility for leadership into the organization's risk posture.
- Difficulty adapting to changing regulatory landscapes.

### Why Existing Solutions Fall Short

While comprehensive GRC tools exist (e.g., MetricStream, Drata), they often come with high costs, vendor lock-in, and a lack of the specific, deep customizability required for the user flows and AI-powered gap analysis envisioned for this project. A custom-built solution is necessary to deliver a tailored experience that perfectly matches the specified workflows and data models.

### Proposed Solution

A web-based application built on a modern tech stack (Next.js, FastAPI, Supabase) that provides:
- A centralized platform for documenting and monitoring business processes, risks, and controls.
- A key feature to map internal controls to external regulations, enabling automated gap analysis.
- An AI-assisted workflow to analyze regulatory documents, suggest relevant business processes and risks, and recommend controls.
- A real-time dashboard for high-level risk monitoring.

### Key Differentiators

- **Deep, Custom AI Integration:** Unlike generic GRC tools, the AI is tailored to the specific workflow of analyzing regulations and suggesting actionable compliance steps.
- **User-Centric Design:** The platform is designed around specific, intuitive user flows for different roles (Admin, BPO, Executive), rather than a one-size-fits-all approach.
- **High Customizability:** As a custom-built solution, it offers complete control over features, data models, and future development, avoiding the rigidity of off-the-shelf products.

---

## Target Users

### Primary Users

- **Compliance Officers / Managers:** Responsible for the overall compliance framework, defining controls, and reporting.
- **Business Process Owners:** Department heads responsible for implementing and maintaining controls.
- **Executives / Senior Leadership:** Need high-level dashboard views to understand the organization's risk posture.
- **Board of Directors:** Reviews the final risk matrix report.
- **General User:** Needs to view and understand processes, risks, and controls relevant to their work.

---

## Success Metrics

### Business Objectives

- Replace manual, spreadsheet-based risk management processes.
- Improve the accuracy and efficiency of compliance and audit activities.
- Provide real-time visibility into the organization's risk and compliance posture.

### Key Performance Indicators

- Reduction in time spent preparing for audits.
- Increase in the percentage of regulatory requirements covered by internal controls.
- High adoption and satisfaction rates among all user roles.

---

## MVP Scope

### Core Features

- **Simple Role-Based Authentication:** Support for Admin, Business Process Owner, Executive, and General User roles with basic permissions.
- **Flexible Data Table with CRUD:** A comprehensive table for the core risk matrix.
- **Risk Register & Control Library with CRUD:** Centralized places to document and manage risks and controls.
- **Dashboard & Reporting:** A visual dashboard showing the overall risk posture.
- **Regulatory Framework Mapping:** Ability to map controls to specific requirements from different regulations for gap analysis.
- **Powerful Filtering and Sorting:** Multi-select filters and free-text search on the main data table.
- **AI-Assisted Workflow:** Leverage AI to analyze regulatory documents, suggest business processes and risks, and recommend controls.

### Out of Scope for MVP

- **Automated Data Migration/Import:** The initial release will assume manual data entry. This is a "fast-follow" feature.
- **Automated Notifications:** Email reminders for tasks are a post-MVP feature.
- **Granular, Position-Based RBAC:** The MVP will use simple role-based access; fine-grained permissions will be implemented later.
- **Advanced PDF Reporting:** The MVP will rely on browser print-to-PDF functionality.
- **Gamification and advanced user feedback channels.**

### MVP Success Criteria

- A Compliance Officer can successfully create a control, link it to a regulation, have it assessed, and an Executive can view the result in a report.
- Role-based access is enforced (e.g., a General User cannot perform admin actions).
- All critical changes to controls and assessments are logged in an audit trail.
- The system can generate a readable report of the current risk matrix.
- The system can generate a gap analysis report for a selected regulation.

---

## Market Context

### Market Analysis

The Governance, Risk, and Compliance (GRC) software market is mature, with established enterprise players like MetricStream and IBM OpenPages, and newer, AI-focused platforms like Drata. While these tools are feature-rich, they often come with high subscription costs and a level of complexity and rigidity that makes them a poor fit for organizations seeking a highly tailored, intuitive solution. The opportunity for this project lies in providing a more focused, customizable, and user-friendly alternative that leverages AI in a more deeply integrated way than generic solutions.

---

## Technical Preferences

### Technical Stack

- **Frontend:** Next.js 14+ with TypeScript, Tailwind CSS, Shadcn UI, Zustand, and Recharts. Deployed on **Vercel**.
- **Backend:** FastAPI (Python) with SQLAlchemy and Alembic. Deployed on **Railway** to support long-running AI tasks.
- **Database & BaaS:** **Supabase** (PostgreSQL) for the database, authentication, and real-time capabilities.
- **AI Orchestration:** **Pydantic-AI** to ensure reliable, structured JSON output from LLMs (e.g., OpenAI GPT-4).

### Rationale

This stack was chosen for its modern, scalable architecture. The separation of frontend and backend allows for independent development and deployment. Supabase accelerates development by providing key backend services. The choice of Railway for the backend and Pydantic-AI for orchestration directly mitigates the primary technical risks of serverless timeouts and unstructured AI output.

---

## Risks and Assumptions

### Key Risks

- **AI Integration Complexity:** Ensuring consistent and accurate results from AI prompts requires significant testing and refinement.
  - *Mitigation:* Use Pydantic-AI for structured output and implement a "human-in-the-loop" validation workflow for all AI suggestions.
- **Scope Creep:** The feature-rich proposal could exceed the 4-week MVP timeline.
  - *Mitigation:* Strict adherence to the defined MVP scope, with a willingness to defer "nice-to-have" features.
- **Integration Complexity:** Securely connecting Vercel, Railway, and Supabase requires careful management of environment variables and CORS policies.
  - *Mitigation:* Address this early in the architecture phase with clear documentation and testing.

### Assumptions

- AI-assisted development will increase productivity by 40-50% for routine coding tasks.
- The chosen tech stack (Supabase, Railway, FastAPI) can handle the expected user load.
- The 4-week MVP timeline is achievable with a focused scope and AI assistance.

---

## Timeline

The project will follow the 4-phase BMAD-methodology, with an estimated total duration of 4 weeks for the MVP.

- **Weeks 1-2:** Analyze, Plan, Architect, and Design.
- **Weeks 3-4:** Develop, Test, and Deploy.

---

## Supporting Materials

- `proposal.md`
- `brainstorming-session 1-results-Saturday, November 8, 2025.md`
- `brainstorming-session 2-results-Saturday, November 8, 2025.md`
- `research-2025-11-08 buy-vs-build-analysis.md`
- `research-technical-2025-11-16 LLM Orchestration.md`
- `research-technical-2025-11-17 Backend Deployment Strategy.md`
- `research-technical-2025-11-17-tech-stack-analysis.md`

---

_This Product Brief captures the vision and requirements for the Risk Control Matrix project._

_It was created through collaborative discovery and reflects the unique needs of this Enterprise SaaS Application project._

_Next: The PRD workflow will transform this brief into detailed product requirements._
