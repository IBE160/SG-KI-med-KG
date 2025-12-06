# Epic Technical Specification: AI-Powered Gap Analysis & Auditing

Date: Friday, December 5, 2025
Author: BIP
Epic ID: 3
Status: Draft

---

## Overview

This epic delivers the core value proposition of the ibe160 platform: the "AI Legal Specialist." It enables the system to analyze regulatory documents, identify potential risks and controls, and present them for human validation. Additionally, it implements an immutable audit trail to record all critical compliance actions. This transforms the platform from a passive database into an intelligent, proactive compliance partner.

## Objectives and Scope

**Objectives:**
*   Enable automated analysis of regulatory documents (PDF/Text) using LLMs.
*   Implement a "Human-in-the-Loop" (HITL) workflow for validating AI suggestions.
*   Establish a tamper-proof audit log for all critical data changes.

**In Scope:**
*   Secure file upload and storage (Supabase Storage).
*   Asynchronous document processing pipeline (Celery/Redis).
*   AI integration using OpenAI GPT-4 via Pydantic-AI for structured output (Single provider PoC).
*   Backend API endpoints for upload, analysis status, and suggestion management.
*   Frontend UI for document upload and the two-stage "AI Review Mode" (CO Triage).
*   Database schema for audit logs and triggers/logic to populate them.
*   Integration with existing core data models (Risks, Controls).

**Out of Scope:**
*   OCR for scanned images (text extraction assumes selectable text PDF or plain text).
*   Autonomous AI decision-making (all suggestions require human approval).
*   Advanced specialized legal models (using general purpose GPT-4 with prompt engineering).
*   BPO final approval workflow (covered in Epic 4).

## System Architecture Alignment

This epic leverages the **AI & Vector Database** and **Background Jobs** architectural decisions.
*   **Frontend:** Next.js components for upload and review, communicating via REST API.
*   **Backend:** FastAPI endpoints handle uploads and trigger Celery tasks.
*   **Storage:** Supabase Storage for files.
*   **Database:** PostgreSQL with `pgvector` (future proofing) and standard tables for suggestions and audit logs.
*   **AI Service:** Dedicated service layer interacting with OpenAI API.
*   **Queue:** Redis/Celery for decoupling long-running analysis from the request lifecycle.

## Detailed Design

### Services and Modules

*   **Document Service (`backend/app/services/document_service.py`):** Handles file validation, storage uploads, and metadata creation.
*   **AI Service (`backend/app/services/ai_service.py`):** Manages interaction with OpenAI, prompt engineering, and structured response parsing.
*   **Analysis Task (`backend/tasks/analysis.py`):** Celery task that orchestrates the analysis pipeline (Download -> Extract Text -> AI Process -> Save Suggestions).
*   **Audit Service (`backend/app/services/audit_service.py`):** centralized logic for recording audit log entries.
*   **Review UI (`frontend/components/custom/ai-review-mode`):** React components for the split-view triage interface.

### Data Models and Contracts

**New Entities:**

*   **`documents`**:
    *   `id`: UUID (PK)
    *   `filename`: String
    *   `storage_path`: String
    *   `status`: Enum (pending, processing, completed, failed)
    *   `uploaded_by`: UUID (FK to users)
    *   `created_at`: Timestamp

*   **`ai_suggestions`**:
    *   `id`: UUID (PK)
    *   `document_id`: UUID (FK to documents)
    *   `type`: Enum (risk, control)
    *   `content`: JSONB (Structured suggestion data)
    *   `rationale`: Text
    *   `source_reference`: Text (Clause/Section)
    *   `status`: Enum (pending, accepted, rejected)
    *   `created_at`: Timestamp

*   **`audit_logs`**:
    *   `id`: UUID (PK)
    *   `action`: String (e.g., "CREATE_CONTROL", "APPROVE_SUGGESTION")
    *   `entity_type`: String
    *   `entity_id`: UUID
    *   `actor_id`: UUID (FK to users)
    *   `changes`: JSONB (Old/New values)
    *   `timestamp`: Timestamp

### APIs and Interfaces

*   `POST /api/v1/documents/upload`: Upload a file. Returns `document_id`.
*   `GET /api/v1/documents/{id}/status`: Check processing status.
*   `GET /api/v1/documents/{id}/suggestions`: Retrieve generated suggestions.
*   `POST /api/v1/suggestions/{id}/approve`: CO promotes a suggestion (moves to BPO queue).
*   `POST /api/v1/suggestions/{id}/reject`: CO dismisses a suggestion.
*   `GET /api/v1/audit-logs`: Retrieve audit history (filterable).

### Workflows and Sequencing

**Document Analysis:**
1.  **Admin** uploads file -> **API** saves to Storage -> **API** creates `document` record -> **API** triggers Celery task.
2.  **Celery Worker** picks up task -> Downloads file -> Extracts text -> Sends prompt to **OpenAI**.
3.  **OpenAI** returns structured JSON -> **Worker** parses and saves `ai_suggestions`.
4.  **Worker** updates `document` status to `completed`.

**CO Triage:**
1.  **CO** views suggestions -> Selects "Approve" -> **API** updates suggestion status -> **API** creates/links preliminary Risk/Control entity -> **API** logs audit entry.

## Non-Functional Requirements

### Performance

*   **File Upload:** Support files up to 20MB.
*   **Analysis Time:** Provide feedback on expected processing time. Long documents should not timeout the request (handled by async queue).
*   **UI Responsiveness:** Review interface must handle 50+ suggestions without lag.

### Security

*   **Malware Scan:** (Recommended) Files should ideally be scanned.
*   **Access Control:** Only Admins/COs can upload and review.
*   **Data Privacy:** Ensure uploaded documents are only accessible to authorized tenants (RLS).

### Reliability/Availability

*   **Retry Logic:** Celery tasks should retry on transient AI API failures.
*   **Error Handling:** Graceful degradation if AI service is unavailable (queueing).

### Observability

*   **Logging:** detailed logs for analysis pipeline stages.
*   **Metrics:** Track token usage and processing time per document.

## Dependencies and Integrations

*   **OpenAI API:** GPT-4 model access.
*   **Supabase Storage:** File persistence.
*   **Celery & Redis:** Async task management.
*   **Pydantic-AI:** Structured data validation from LLM.
*   **Python Libraries:** `pypdf` (or similar) for text extraction.

## Acceptance Criteria (Authoritative)

**Story 3.1: Document Upload**
*   Admin can upload PDF/Text files via UI.
*   File is securely stored in Supabase bucket.
*   Metadata record created in DB.
*   User sees "Processing" status.

**Story 3.2: AI Analysis**
*   System extracts text from uploaded file.
*   LLM processes text and identifies Risks and Controls.
*   Output is valid JSON matching the schema.
*   Suggestions are saved to DB linked to the document.
*   Rationales cite specific sections of the source text.

**Story 3.3: HITL Interface**
*   Two-pane view: List of suggestions vs Details.
*   CO can "Accept" (promote) or "Reject" (dismiss).
*   Accepted items trigger notification (mocked or real) for BPO.
*   UI updates immediately upon action.

**Story 3.4: Audit Trail**
*   `audit_logs` table captures CREATE/UPDATE/DELETE on Risks/Controls.
*   Captures "Approve Suggestion" actions.
*   Log entry includes Actor, Timestamp, Action, and Diff.
*   Logs are immutable (enforced by DB policy or application logic).

## Traceability Mapping

| AC ID | Spec Section | Component | Test Idea |
| :--- | :--- | :--- | :--- |
| AC-3.1.1 | APIs/Interfaces | Upload Endpoint | Upload valid PDF, verify 200 OK & DB record |
| AC-3.2.1 | Services/AI | Analysis Task | Mock OpenAI, verify text extraction & prompt construction |
| AC-3.3.1 | Detailed Design | Review UI | Click "Accept", verify API call & list update |
| AC-3.4.1 | Data Models | Audit Service | Perform DB update, verify `audit_logs` entry exists |

## Risks, Assumptions, Open Questions

*   **Risk:** AI hallucinations or poor quality suggestions.
    *   *Mitigation:* Prompt engineering refinement and mandatory human review.
*   **Assumption:** Uploaded documents are text-selectable PDFs, not scanned images.
*   **Question:** Specific formatting requirements for "Source Reference" (e.g., Page # vs Section Header)?

## Test Strategy Summary

*   **Unit Tests:** Service methods (upload, prompt generation, audit logging).
*   **Integration Tests:** API endpoints (upload -> queue -> status).
*   **E2E Tests:** Full flow: Upload document -> Wait for analysis -> Review suggestion -> Check audit log.

## Post-Review Follow-ups

*   [ ] **Story 3.1:** [High] Implement missing integration test for successful document upload (AC #1).
*   [ ] **Story 3.1:** [Med] Improve file validation to check magic bytes instead of just content-type header (AC #1).
*   [ ] **Story 3.1:** [Low] Update `get_documents_by_user` to explicitly filter by `tenant_id` (AC #4).
*   [ ] **Story 3.1:** [Med] Wrap `DocumentsPage` with `RoleGuard` to enforce admin access on client-side (Frontend Pattern) (AC #1).
*   [ ] **Story 3.2:** [Low] Refine AI error handling to distinguish between retryable API errors and hard failures (AC #2).
*   [ ] **Story 3.2:** [Low] Implement robust chunking strategy for documents larger than LLM context window (AC #2).
