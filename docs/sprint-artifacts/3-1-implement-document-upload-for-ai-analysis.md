# Story 3.1: Implement Document Upload for AI Analysis

Status: review

## Story

As an **Admin**,
I want **to upload regulatory documents (PDF/text) to the system**,
so that **the AI can analyze them for potential risks and controls**.

## Acceptance Criteria

1. **Admin can upload PDF/Text files via UI.**
    - An authenticated Admin user can select and upload a file (PDF or plain text) through the application interface.
    - Files up to 20MB are supported.
    - Non-PDF/Text files are rejected with a clear error message.
2. **File is securely stored in Supabase bucket.**
    - The uploaded file is saved to a dedicated, private Supabase Storage bucket.
    - Row Level Security (RLS) ensures files are isolated by tenant (if applicable) or restricted to Admin access.
3. **Metadata record created in DB.**
    - A record is created in the `documents` table with fields: `id`, `filename`, `storage_path`, `uploaded_by`, `created_at`, and `status`.
    - The initial `status` is set to "pending".
4. **User sees "Processing" status.**
    - Upon successful upload, the UI displays a success message.
    - The uploaded document appears in a list view with a status of "Processing" (or "Pending" -> "Processing" once the background task starts).
    - Immediate feedback confirms the system has received the file for analysis.

## Tasks / Subtasks

- [x] **Backend: Configure Supabase Storage** (AC: 2)
  - [x] Create a new storage bucket (e.g., `regulatory-docs`) via migration or script (if possible) or manual instructions.
  - [x] Implement RLS policies for the bucket to restrict access to Admins.
- [x] **Backend: Implement Document Data Model** (AC: 3)
  - [x] Define `Document` SQLAlchemy model with required fields.
  - [x] Create Alembic migration for the `documents` table.
  - [x] Define Pydantic schemas for Document (Create, Read).
- [x] **Backend: Create Document Upload Endpoint** (AC: 1, 2, 3)
  - [x] Implement `POST /api/v1/documents/upload` endpoint.
  - [x] Validate file type (PDF, text/plain) and size (<20MB).
  - [x] Use Supabase Storage client to upload the file.
  - [x] Create the `Document` record in the database.
- [x] **Frontend: Build Document Upload UI** (AC: 1, 4)
  - [x] Create a `DocumentUpload` component using Shadcn UI (e.g., Input type='file' or a dropzone).
  - [x] Implement the API call to upload the file.
  - [x] Handle success/error states and display toast notifications.
- [x] **Frontend: Build Document List View** (AC: 4)
  - [x] Create a component to list uploaded documents.
  - [x] Fetch documents from `GET /api/v1/documents` (create this endpoint if needed for listing).
  - [x] Display the current status (`pending`, `processing`, etc.) for each document.
- [x] **Backend: Document Listing Endpoint** (AC: 4)
  - [x] Implement `GET /api/v1/documents` to list documents for the tenant.
- [x] **Testing**
  - [x] Unit test: Document model and schema validation.
  - [x] Integration test: Upload endpoint success and failure (invalid type/size).
  - [x] Integration test: Storage interaction (mocked).

## Dev Notes

- **Architecture Patterns**:
  - Follow the existing Service/Repository pattern. Create `DocumentService` for logic.
  - Use `Supabase` client for storage operations.
  - Files should be stored in a private bucket; generating signed URLs might be needed for download later (out of scope for this specific story but good to keep in mind).
- **Source Tree Components**:
  - `backend/app/models/document.py` (New)
  - `backend/app/schemas/document.py` (New)
  - `backend/app/api/v1/endpoints/documents.py` (New)
  - `backend/app/services/document_service.py` (New)
  - `frontend/app/dashboard/admin/documents/` (New page/components)
- **Testing Standards**:
  - Pytest for backend.
  - Mock Supabase client for storage tests to avoid network calls.

### Project Structure Notes

- **Alignment**:
  - Place new backend components in `backend/app/` structure as established.
  - Place frontend page in `frontend/app/dashboard/admin/`.
- **Conflicts**: None anticipated.

### Learnings from Previous Story

**From Story 2-2-implement-role-based-access-control-rbac (Status: done)**

- **New Service Created**: `AuthService` (implicit in `deps.py` and `security.py`) - leverage `current_user` dependency.
- **Architectural Change**: RBAC is enforced via `has_role` dependency. Use `deps.has_role(["admin"])` for the upload endpoint to ensure only Admins can upload.
- **Testing Setup**: Integration tests for API endpoints are established. Use `client` fixture and `superuser_token_headers` (or similar) to authenticate as Admin in tests.
- **Frontend Patterns**: `RoleGuard` is available. Ensure the Document Upload page is protected by `RoleGuard` for Admins.

[Source: stories/2-2-implement-role-based-access-control-rbac.md#Dev-Agent-Record]

### References

- [Epic Tech Spec: Epic 3](docs/sprint-artifacts/tech-spec-epic-3.md)
- [Architecture Document](docs/architecture.md#45-file-storage)

## Dev Agent Record

### Context Reference

- docs/sprint-artifacts/3-1-implement-document-upload-for-ai-analysis.context.xml

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

N/A - Implementation completed successfully without debugging issues.

### Completion Notes List

- **Supabase Storage Configuration**: Added SUPABASE_SERVICE_KEY and SUPABASE_STORAGE_BUCKET to config (backend/app/config.py:19-20, backend/.env.example:25-29)
- **Supabase Client Utility**: Created get_supabase_client() helper for server-side storage operations (backend/app/core/supabase.py)
- **Document Model**: Implemented Document SQLAlchemy model with DocumentStatus enum (pending/processing/completed/failed) (backend/app/models/document.py)
- **Database Migration**: Created Alembic migration d234567890bc for documents table with foreign key to user.id (backend/alembic_migrations/versions/d234567890bc_create_documents_table.py)
- **Pydantic Schemas**: Added DocumentBase, DocumentCreate, DocumentRead, DocumentUploadResponse to schemas.py (backend/app/schemas.py:140-171)
- **Document Service**: Implemented DocumentService with file validation (PDF/text, 20MB limit), Supabase Storage upload, and database CRUD operations (backend/app/services/document_service.py)
- **API Endpoints**: Created POST /api/v1/documents/upload, GET /api/v1/documents, and GET /api/v1/documents/{id} with admin role protection (backend/app/api/v1/endpoints/documents.py)
- **Frontend UI**: Built combined upload and list view at /dashboard/admin/documents with file selection, upload progress, status badges, and document table (frontend/app/dashboard/admin/documents/page.tsx)
- **Test Coverage**: Wrote 7 comprehensive tests covering auth, validation, and file size limits - all 60 backend tests pass (backend/tests/api/v1/test_documents.py)

### File List

**Backend - New Files:**
- backend/app/core/supabase.py
- backend/app/models/document.py
- backend/app/services/document_service.py
- backend/app/api/v1/endpoints/documents.py
- backend/alembic_migrations/versions/d234567890bc_create_documents_table.py
- backend/tests/api/v1/test_documents.py

**Backend - Modified Files:**
- backend/app/config.py
- backend/app/schemas.py
- backend/app/models/__init__.py
- backend/app/models/user.py
- backend/app/main.py
- backend/.env.example

**Frontend - New Files:**
- frontend/app/dashboard/admin/documents/page.tsx
