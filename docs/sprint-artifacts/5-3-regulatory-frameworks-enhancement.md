# Story 5.3: Regulatory Frameworks Enhancement

Status: drafted

## Story

As an **Admin**,
I want **uploaded regulatory documents to be automatically classified as Main Laws or Regulations by AI, with Regulations linked to parent Laws in a hierarchical structure**,
so that **I can maintain an organized regulatory framework that reflects the actual legal structure (laws → regulations)**.

## Acceptance Criteria

1. **Document Classification During "Process Now"**
   - Given I have uploaded a regulatory document,
   - When I click "Process Now" in the documents page,
   - Then the AI analyzes the document and determines if it is a "Main Law" or a "Regulation".
   - And the AI classification is added to the document processing workflow.

2. **Law Creation/Linking**
   - Given the AI classifies a document as a "Main Law",
   - When the processing completes,
   - Then a `RegulatoryFramework` record is created or updated with the law details.
   - And the document is linked to this framework via `document_id` foreign key.

3. **Regulation Creation with Parent Law Linking**
   - Given the AI classifies a document as a "Regulation",
   - When the processing completes,
   - Then the AI identifies the parent Law that this regulation belongs to.
   - And a `RegulatoryRequirement` record is created linked to the parent `RegulatoryFramework`.
   - And if the parent Law doesn't exist, it is created first.
   - And the document is linked to this requirement via `document_id` foreign key.

4. **Hierarchical Display on Regulatory Frameworks Page**
   - Given regulatory frameworks and requirements exist,
   - When I navigate to `/dashboard/regulatory-frameworks`,
   - Then I see a hierarchical tree view with Laws as parent nodes.
   - And each Law expands to show its associated Regulations as child nodes.
   - And each item shows its linked source document (if any).

5. **One Document, One Framework Item**
   - Given a document is being processed,
   - When the AI creates or links a framework/requirement,
   - Then the document can only be linked to one Law OR one Regulation (not multiple).
   - And attempting to re-process a document updates the existing link rather than creating duplicates.

6. **Manual Override Capability (Future Enhancement)**
   - Given this is an MVP feature,
   - When a user wants to manually override AI classification,
   - Then this capability is noted in Dev Notes as a future enhancement.
   - And the current implementation focuses on AI-driven classification only.

## Tasks / Subtasks

- [ ] **Backend: Update Document Processing AI Prompt** (AC: #1, #2, #3)
  - [ ] Modify AI prompt in `backend/app/services/document_processing_service.py` (or similar)
  - [ ] Add instruction for AI to classify document as "Law" or "Regulation"
  - [ ] Add instruction to identify parent Law name if document is a Regulation
  - [ ] Update prompt to extract framework/requirement details (name, description, version)
  - [ ] Test prompt with sample law and regulation documents

- [ ] **Backend: Extend Document Processing Logic** (AC: #2, #3, #5)
  - [ ] Update document processing workflow to handle AI classification response
  - [ ] Implement logic for "Law" classification:
    - Create or update `RegulatoryFramework` with law details
    - Link document via `document_id`
  - [ ] Implement logic for "Regulation" classification:
    - Query for parent `RegulatoryFramework` by name
    - Create parent Law if doesn't exist
    - Create `RegulatoryRequirement` linked to framework
    - Link document via `document_id`
  - [ ] Ensure document can only link to one framework item (prevent duplicates)
  - [ ] Add validation: reject processing if document already linked

- [ ] **Backend: Update Data Models** (AC: #3, #4)
  - [ ] Verify `RegulatoryFramework` model has necessary fields (from Story 5.2)
  - [ ] Verify `RegulatoryRequirement` model has `framework_id` foreign key (from Story 5.2)
  - [ ] Add `document_id` foreign key to both models if not exists
  - [ ] Create database migration for new fields
  - [ ] Apply migration to dev/test databases

- [ ] **Backend: Create API Endpoint for Hierarchical Data** (AC: #4)
  - [ ] Create `GET /api/v1/regulatory-frameworks/tree` endpoint
  - [ ] Return JSON with frameworks as parents and requirements as children
  - [ ] Include linked document info for each item
  - [ ] Apply tenant filtering (RLS)
  - [ ] Add endpoint tests

- [ ] **Frontend: Update Regulatory Frameworks Page** (AC: #4)
  - [ ] Modify `frontend/app/dashboard/regulatory-frameworks/page.tsx`
  - [ ] Replace flat table view with tree component (Shadcn/UI Collapsible or custom)
  - [ ] Fetch data from `/api/v1/regulatory-frameworks/tree`
  - [ ] Implement expand/collapse functionality for Law nodes
  - [ ] Show Regulations as child nodes under each Law
  - [ ] Display linked document name/link for each item
  - [ ] Maintain existing Create/Edit/Delete functionality

- [ ] **Frontend: Update Document Processing UI** (AC: #1)
  - [ ] Verify "Process Now" button exists in documents page
  - [ ] Add loading state during AI classification
  - [ ] Show classification result to user after processing
  - [ ] Display whether document was classified as Law or Regulation
  - [ ] Show parent Law name if Regulation

- [ ] **Testing** (All ACs)
  - [ ] Backend: Test AI classification prompt with sample documents
  - [ ] Backend: Test Law creation from document
  - [ ] Backend: Test Regulation creation with parent linking
  - [ ] Backend: Test parent Law auto-creation
  - [ ] Backend: Test duplicate document linking prevention
  - [ ] Frontend: Test tree view rendering
  - [ ] Frontend: Test expand/collapse behavior
  - [ ] E2E: Test complete flow from document upload → Process Now → tree view display

## Dev Notes

### Architecture Patterns

**Data Model (From Story 5.2):**
The data model has been refactored to separate:
- `RegulatoryFramework`: Parent frameworks (e.g., "GDPR", "SOX")
- `RegulatoryRequirement`: Individual requirements within a framework (e.g., "Article 32")

**For this story:**
- "Main Law" → maps to `RegulatoryFramework`
- "Regulation" → maps to `RegulatoryRequirement` with `framework_id` FK to parent Law
- This aligns with existing Story 5.2 data model (no schema changes needed, just add `document_id` FK)

**Document Processing:**
- Current flow: Upload → Store in Supabase Storage → AI analyzes → Creates suggestions
- Enhanced flow: Upload → Store → AI analyzes + classifies (Law/Regulation) → Creates framework/requirement + suggestions

**AI Prompt Enhancement:**
- Add classification task to existing document analysis prompt
- Extract: document_type ("Law" | "Regulation"), parent_law_name (if Regulation), framework_details (name, description, version)
- Use Pydantic-AI structured output for classification

**API Design:**
- New endpoint: `GET /api/v1/regulatory-frameworks/tree` - Returns hierarchical JSON
- Alternative: Enhance existing `/api/v1/regulatory-frameworks` with `?view=tree` query param
- Frontend uses tree data to build collapsible UI

**Frontend Components:**
- Shadcn/UI Collapsible component for tree nodes
- Similar pattern to Overview page tree view (Story 4.6)
- Maintain existing CRUD operations (Create/Edit/Delete)

### Project Structure Notes

**Files to Create:**
- `backend/app/api/v1/endpoints/regulatory_frameworks.py` - Tree endpoint (if doesn't exist)
- `frontend/app/dashboard/regulatory-frameworks/components/FrameworkTree.tsx` (optional) - Tree component

**Files to Modify:**
- `backend/app/services/document_processing_service.py` - Add AI classification logic
- `backend/app/models/compliance.py` - Add `document_id` FK to RegulatoryFramework and RegulatoryRequirement
- `backend/alembic/versions/` - New migration for document_id FK
- `frontend/app/dashboard/regulatory-frameworks/page.tsx` - Replace table with tree view
- `frontend/app/dashboard/admin/documents/page.tsx` - Show classification results

**Existing Models to Reuse (From Story 5.2):**
- `RegulatoryFramework` (parent) - in `backend/app/models/compliance.py`
- `RegulatoryRequirement` (child) - in `backend/app/models/compliance.py`
- Relationship: `RegulatoryFramework.requirements` → One-to-Many → `RegulatoryRequirement.framework_id`

### Learnings from Previous Story (5-2)

**From Story 5-2-develop-gap-analysis-report-generation (Status: done)**

- **Critical Data Model Refactor**: Story 5.2 introduced the separation of `RegulatoryFramework` (parent) and `RegulatoryRequirement` (child)
  - Previous issue: Single table represented both concepts, causing logic flaws
  - Fix: Two-table design with 1:many relationship via `framework_id` FK
  - Location: `backend/app/models/compliance.py:97-121`
  - **Action for this story**: Use existing Framework/Requirement model instead of creating new hierarchical structure

- **Hierarchical Relationship Pattern**: Framework → Requirements relationship already exists
  - Gap Analysis Service queries this relationship (LEFT JOIN pattern)
  - Location: `backend/app/services/gap_analysis_service.py:61-79`
  - **Action for this story**: Extend this relationship to include document links

- **Tree View UI Pattern**: Gap Analysis page displays hierarchical data
  - Location: `frontend/app/dashboard/reports/gap-analysis/page.tsx`
  - Uses framework selection and requirement display
  - **Action for this story**: Apply similar tree pattern to regulatory frameworks page

- **Pydantic-AI Structured Output**: Story 5.2 uses Pydantic schemas for API responses
  - Pattern: Define schema → AI/Service returns structured data → Frontend consumes typed response
  - Location: `backend/app/schemas/reports.py`
  - **Action for this story**: Use Pydantic-AI for document classification output

- **Testing with Real Data**: Previous story moved from mocks to real database seeding
  - Test pattern: Seed frameworks and requirements → Run queries → Verify results
  - Location: `backend/tests/api/v1/test_reports.py:19-72`
  - **Action for this story**: Use similar integration test pattern for classification logic

- **Authorization Pattern**: Admin/Executive role checking well-established
  - Function: `verify_admin_or_executive_role()`
  - Location: `backend/app/api/v1/endpoints/reports.py:14-20`
  - **Action for this story**: Document processing likely Admin-only (verify requirements)

**Files Modified in Story 5.2:**
- `backend/app/models/compliance.py` - RegulatoryFramework and RegulatoryRequirement models
- `backend/app/services/gap_analysis_service.py` - Hierarchical query pattern
- `backend/app/schemas/reports.py` - Pydantic schema patterns
- `frontend/app/dashboard/reports/gap-analysis/page.tsx` - Framework selection UI
- `frontend/hooks/useGapAnalysis.ts` - React Query with 60s TTL

[Source: docs/sprint-artifacts/5-2-develop-gap-analysis-report-generation.md#Dev-Notes, #Learnings-from-Previous-Story]

### AI Prompt Design

**Classification Prompt Structure:**
```python
# Add to existing document analysis prompt:
"""
Additionally, classify this document as one of the following:
1. "Main Law" - A primary legal framework or regulation (e.g., GDPR, SOX, HIPAA)
2. "Regulation" - A specific requirement, article, or section within a Main Law

If classified as "Regulation", identify the parent Main Law it belongs to.

Extract the following structured data:
- document_type: "Law" | "Regulation"
- framework_name: str (name of the law or regulation)
- framework_description: str (brief description)
- parent_law_name: str | None (required if document_type is "Regulation")
- version: str | None (version number if applicable)
"""
```

**Pydantic Schema for AI Response:**
```python
class DocumentClassification(BaseModel):
    document_type: Literal["Law", "Regulation"]
    framework_name: str
    framework_description: str
    parent_law_name: str | None
    version: str | None
```

### Security & Validation

**Document Linking Constraints:**
- One document can only be linked to ONE framework or requirement
- Enforce unique constraint: `UNIQUE(document_id)` on both tables (or check before insert)
- Prevent re-processing if document already has classification (update instead of create)

**Tenant Isolation:**
- All framework/requirement queries filter by `tenant_id` (RLS)
- Document uploads already scoped to tenant (from Epic 3)
- Cross-tenant framework linking not possible

**Authorization:**
- Document upload and processing: Admin or Compliance Officer roles
- Regulatory frameworks CRUD: Admin only
- Tree view: All authenticated users (read-only)

### References

- [PRD - Regulatory Mapping](../PRD.md#mvp---minimum-viable-product) - Linking controls to regulations
- [PRD - AI-Assisted Workflow](../PRD.md#mvp---minimum-viable-product) - AI analyzes uploaded documents
- [Architecture - AI Application](../architecture.md#43-ai--vector-database) - OpenAI GPT-4, Pydantic-AI
- [Architecture - File Storage](../architecture.md#45-file-storage) - Supabase Storage for documents
- [Epic 3 - Story 3.1](../epics.md#story-31-implement-document-upload-for-ai-analysis) - Document upload workflow
- [Epic 3 - Story 3.2](../epics.md#story-32-integrate-ai-for-document-analysis--suggestion-generation) - AI analysis with Pydantic-AI
- [Epic 5 - Story 5.1](../epics.md#story-51-implement-many-to-many-compliance-mapping-ui) - Controls-requirements mapping
- [Epic 5 - Story 5.2](../epics.md#story-52-develop-gap-analysis-report-generation) - Framework/Requirement data model

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

<!-- To be filled by dev agent -->

### Debug Log References

<!-- To be filled by dev agent during implementation -->

### Completion Notes List

<!-- To be filled by dev agent upon completion -->

### File List

<!-- To be filled by dev agent with NEW/MODIFIED/DELETED files -->

## Change Log

- 2025-12-15: Story drafted by SM agent (Bob) in YOLO mode
