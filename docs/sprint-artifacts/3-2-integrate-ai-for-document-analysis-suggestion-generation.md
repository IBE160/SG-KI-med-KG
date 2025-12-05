# Story 3.2: Integrate AI for Document Analysis & Suggestion Generation

Status: ready-for-dev

## Story

As a **system**,
I want **to use AI (LLM) to analyze uploaded regulatory documents**,
so that **I can generate suggestions for risks and controls**.

## Acceptance Criteria

1. **System extracts text from uploaded file.**
    - The system can process PDF and plain text files stored in Supabase Storage.
    - Text content is accurately extracted from the document.
    - The system handles potential extraction errors (e.g., corrupted files, encrypted PDFs) gracefully.
2. **LLM processes text and identifies Risks and Controls.**
    - The extracted text is sent to an LLM (OpenAI GPT-4) with a specific prompt to identify risks and controls.
    - The prompt enforces the "AI Legal Specialist" persona.
    - The processing respects token limits (e.g., by chunking large documents if necessary).
3. **Output is valid JSON matching the schema.**
    - The LLM response is structured as a JSON object containing a list of suggestions.
    - The schema strictly adheres to the defined `Suggestion` model (type: risk/control, content, rationale, source_reference).
    - Pydantic-AI (or similar validation) ensures the output format is correct.
4. **Suggestions are saved to DB linked to the document.**
    - Each valid suggestion is saved to the `ai_suggestions` table.
    - Suggestions are linked to the original `document_id`.
    - Initial status of suggestions is "pending".
5. **Rationales cite specific sections of the source text.**
    - Every suggestion includes a `rationale` explaining why it was generated.
    - Every suggestion includes a `source_reference` (e.g., "Section 4.2", "Page 3, Paragraph 1") verbatim from the document or a clear pointer.

## Tasks / Subtasks

- [ ] **Backend: Implement AI Service** (AC: 2, 3, 5)
  - [ ] Create `backend/app/services/ai_service.py`.
  - [ ] Implement `analyze_document(text: str)` method.
  - [ ] Define the system prompt for "AI Legal Specialist".
  - [ ] Configure OpenAI client with API key.
  - [ ] Use Pydantic to define the expected output schema (`AnalysisResult`, `Suggestion`).
- [ ] **Backend: Implement Text Extraction** (AC: 1)
  - [ ] Add `pypdf` (or similar) dependency.
  - [ ] Implement logic to download file from Supabase Storage.
  - [ ] Implement text extraction for PDF and text files.
- [ ] **Backend: Implement Celery Analysis Task** (AC: 1, 2, 3, 4)
  - [ ] Create `backend/tasks/analysis.py`.
  - [ ] Define `process_document(document_id: UUID)` task.
  - [ ] Implement the pipeline: Download -> Extract -> Analyze (AI) -> Save.
  - [ ] Handle errors and update `document.status` (processing -> completed/failed).
- [ ] **Backend: Implement Suggestion Data Model** (AC: 4)
  - [ ] Define `AISuggestion` SQLAlchemy model in `backend/app/models/suggestion.py`.
  - [ ] Create Alembic migration for `ai_suggestions` table.
  - [ ] Define Pydantic schemas in `backend/app/schemas/suggestion.py`.
- [ ] **Backend: Trigger Analysis on Upload**
  - [ ] Update `POST /api/v1/documents/upload` to trigger the Celery task after successful upload.
- [ ] **Testing**
  - [ ] Unit test: Text extraction logic (with mock files).
  - [ ] Unit test: AI Service prompt generation and schema validation (mock OpenAI).
  - [ ] Integration test: Full Celery task execution (mocking external calls).

## Dev Notes

- **Architecture Patterns**:
  - **Asynchronous Processing**: Use Celery for the long-running analysis task. Ensure Redis is configured as the broker.
  - **AI Integration**: Use `Pydantic` models to define the structure of the LLM response (Function Calling or JSON mode).
  - **Service Layer**: Keep the AI logic in `ai_service.py` and document handling in `document_service.py` (or similar).
- **Source Tree Components**:
  - `backend/app/services/ai_service.py` (New)
  - `backend/tasks/analysis.py` (New)
  - `backend/app/models/suggestion.py` (New)
  - `backend/app/schemas/suggestion.py` (New)
- **Testing Standards**:
  - **Mocking**: Extremely important here. Do NOT make real calls to OpenAI in tests. Mock the `openai.ChatCompletion.create` (or equivalent) method.
  - **Fixtures**: Use sample PDF/text files for extraction tests.

### Project Structure Notes

- **Alignment**:
  - Tasks go in `backend/tasks/`.
  - Services in `backend/app/services/`.
  - Models/Schemas in standard locations.
- **Conflicts**: None.

### Learnings from Previous Story

**From Story 3-1-implement-document-upload-for-ai-analysis (Status: ready-for-dev)**

- **New Files**: `Document` model and `DocumentService` should exist (or will be created in 3.1).
- **Dependencies**: `supabase` client is configured.
- **Pattern**: Use the existing `Document` model to update status.
- **Warning**: Ensure 3.1 is fully implemented before starting this, or coordinate closely if working in parallel (Database schema for `documents` is a dependency).

[Source: stories/3-1-implement-document-upload-for-ai-analysis.md#Dev-Agent-Record]

### References

- [Epic Tech Spec: Epic 3](docs/sprint-artifacts/tech-spec-epic-3.md)
- [Architecture Document](docs/architecture.md#43-ai--vector-database)
- [Architecture Document](docs/architecture.md#46-background-jobs)

## Dev Agent Record

### Context Reference

- docs/sprint-artifacts/3-2-integrate-ai-for-document-analysis-suggestion-generation.context.xml

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
