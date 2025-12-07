# Story 4.3: Develop Streamlined Control Assessment Workflow for BPOs

Status: drafted

## Story

As a **Business Process Owner (BPO)**,
I want **a dedicated interface to review and act on AI-promoted suggestions with approve, edit, or discard options**,
so that **I can efficiently assess and add controls/risks to the register with proper residual risk categorization**.

## Acceptance Criteria

### AC-4.4: BPO Pending Reviews Interface

1. BPO user can click "Pending Reviews" card and navigate to `/dashboard/bpo/reviews`
2. Pending reviews page displays paginated list of all suggestions with status "pending_review" assigned to the logged-in BPO
3. List prominently displays Business Process, Risk, and Control names for each suggestion
4. BPO can click on a suggestion to open detailed review screen
5. Detail screen displays all AI-suggested data (risk description, control description, business process, owner) in editable form fields
6. Detail screen displays persistent `source_reference` link to original document clause
7. Non-BPO users attempting to access `/dashboard/bpo/reviews` receive 403 Forbidden error

### AC-4.5: BPO Assessment - Approve Action

1. BPO can select residual risk (low/medium/high) from dropdown on review detail screen
2. Residual risk selection is mandatory before "Approve" button is enabled
3. When BPO clicks "Approve", frontend sends `POST /api/v1/assessments/{id}/assess` with `action: approve` and `residual_risk`
4. Backend validates residual_risk is present; returns 400 Bad Request if missing
5. Backend creates active records in `business_processes`, `risks`, and `controls` tables with approved data
6. Backend updates suggestion status to "active"
7. Backend creates audit log entry with action="approve", user_id, suggestion_id, residual_risk, timestamp
8. Frontend displays success toast: "✅ Successfully added to register" with link to view active item
9. Suggestion is removed from pending reviews list

### AC-4.6: BPO Assessment - Edit Action

1. BPO can click "Edit" button to enable inline editing of form fields
2. BPO can modify risk description, control description, and business process fields
3. Frontend tracks all edits in local state
4. When BPO approves after editing, frontend sends edited values in `AssessmentRequest` payload
5. Backend creates active records with edited values (not original AI-suggested values)
6. Audit log records both approval action AND field-level changes (original vs. edited values)
7. Change log is visible when viewing the active item

### AC-4.7: BPO Assessment - Discard Action

1. BPO can click "Discard" button on review detail screen
2. Frontend displays confirmation modal: "Are you sure? This will archive the suggestion."
3. When BPO confirms, frontend sends `POST /api/v1/assessments/{id}/assess` with `action: discard`
4. Backend updates suggestion status to "archived"
5. Backend creates audit log entry with action="discard"
6. Frontend displays toast: "🗑️ Item discarded"
7. BPO returns to pending reviews list, discarded item removed

### AC-4.8: Authorization and Tenant Isolation

1. All dashboard and assessment endpoints require valid JWT in Authorization header; return 401 if missing/invalid
2. BPO can only assess suggestions where `assigned_bpo_id` matches their user ID; return 403 otherwise
3. All database queries enforce Row-Level Security filtering by `tenant_id`
4. BPO from Tenant A cannot view or assess suggestions from Tenant B (404 returned)

### AC-4.9: Audit Trail Integration

1. All BPO assessment actions (approve, edit, discard) create immutable audit log entry
2. Audit log includes: user_id, action, suggestion_id, timestamp, details (residual_risk, edits if any)
3. If audit logging fails, entire assessment transaction rolls back (data consistency)

## Tasks / Subtasks

- [ ] **Backend: Implement Assessment Data Model** (AC: 4.5, 4.6, 4.7)
  - [ ] Create Pydantic schemas in `backend/app/schemas/assessment.py` (`ResidualRisk` enum, `AssessmentAction` enum, `AssessmentRequest`, `AssessmentResponse`)
  - [ ] Define request/response contracts for assessment endpoint
- [ ] **Backend: Implement Assessment Service** (AC: 4.5, 4.6, 4.7, 4.9)
  - [ ] Create `backend/app/services/assessment_service.py`
  - [ ] Implement `approve_suggestion(db, suggestion_id, residual_risk, edits, actor_id)` method
  - [ ] Implement `discard_suggestion(db, suggestion_id, actor_id)` method
  - [ ] Create active records (business_process, risk, control) with approved/edited data
  - [ ] Update suggestion status to "active" or "archived"
  - [ ] Integrate with AuditService to log all assessment actions
  - [ ] Ensure atomic transactions (rollback if audit logging fails)
- [ ] **Backend: Implement Assessment API Endpoints** (AC: 4.4, 4.5, 4.6, 4.7, 4.8)
  - [ ] Create `GET /api/v1/assessments/pending` in `backend/app/api/v1/endpoints/assessments.py`
  - [ ] Return paginated list of suggestions with status "pending_review" filtered by assigned_bpo_id
  - [ ] Create `POST /api/v1/assessments/{suggestion_id}/assess` endpoint
  - [ ] Validate request payload (AssessmentRequest)
  - [ ] Extract user info from JWT, verify user is BPO
  - [ ] Verify suggestion.assigned_bpo_id matches user_id (return 403 if mismatch)
  - [ ] Call AssessmentService methods based on action (approve/discard)
  - [ ] Return AssessmentResponse with success/failure and audit_log_id
- [ ] **Frontend: Implement BPO Pending Reviews List Page** (AC: 4.4)
  - [ ] Create `frontend/app/(dashboard)/bpo/reviews/page.tsx`
  - [ ] Fetch pending reviews via `GET /api/v1/assessments/pending` using React Query
  - [ ] Display paginated table with Business Process, Risk, Control columns
  - [ ] Implement pagination controls
  - [ ] Make each row clickable to navigate to detail screen
- [ ] **Frontend: Implement BPO Review Detail Page** (AC: 4.4, 4.5, 4.6, 4.7)
  - [ ] Create `frontend/app/(dashboard)/bpo/reviews/[id]/page.tsx`
  - [ ] Fetch suggestion details by ID
  - [ ] Display all AI-suggested data in form fields (initially read-only)
  - [ ] Display `source_reference` link to original document clause
  - [ ] Implement residual risk dropdown (low/medium/high)
  - [ ] Implement "Edit" button to enable inline editing
  - [ ] Implement "Approve" button (enabled only when residual risk selected)
  - [ ] Implement "Discard" button with confirmation modal
- [ ] **Frontend: Implement Approve Flow** (AC: 4.5, 4.6)
  - [ ] When "Approve" clicked, send `POST /api/v1/assessments/{id}/assess` with `action: approve`, `residual_risk`, and any edits
  - [ ] Display success toast with link to active item
  - [ ] Navigate back to pending reviews list
  - [ ] Remove approved item from list (optimistic update or refetch)
- [ ] **Frontend: Implement Discard Flow** (AC: 4.7)
  - [ ] When "Discard" clicked, show confirmation modal
  - [ ] On confirm, send `POST /api/v1/assessments/{id}/assess` with `action: discard`
  - [ ] Display discard toast
  - [ ] Navigate back to pending reviews list
- [ ] **Backend: Implement Authorization Checks** (AC: 4.8)
  - [ ] Verify JWT authentication for all assessment endpoints
  - [ ] Verify user has BPO role (return 403 if not)
  - [ ] Verify suggestion.assigned_bpo_id matches user_id (return 403 if mismatch)
  - [ ] Enforce tenant isolation via RLS
- [ ] **Testing: Unit Tests (Backend)** (AC: 4.5, 4.6, 4.7, 4.9)
  - [ ] Test `AssessmentService.approve_suggestion()` creates active records
  - [ ] Test `AssessmentService.approve_suggestion()` with edits
  - [ ] Test `AssessmentService.discard_suggestion()` updates status to "archived"
  - [ ] Test audit logging integration (all actions logged)
  - [ ] Test transaction rollback if audit logging fails
- [ ] **Testing: Integration Tests (Backend)** (AC: 4.4, 4.5, 4.6, 4.7, 4.8)
  - [ ] Test `GET /api/v1/assessments/pending` returns correct suggestions for BPO
  - [ ] Test `POST /api/v1/assessments/{id}/assess` (approve) end-to-end
  - [ ] Test `POST /api/v1/assessments/{id}/assess` (discard) end-to-end
  - [ ] Test authorization: non-BPO user returns 403
  - [ ] Test authorization: BPO accessing another BPO's suggestion returns 403
  - [ ] Test tenant isolation
- [ ] **Testing: Unit Tests (Frontend)** (AC: 4.4, 4.5, 4.6, 4.7)
  - [ ] Test pending reviews list renders correctly
  - [ ] Test review detail page displays suggestion data
  - [ ] Test "Approve" button disabled until residual risk selected
  - [ ] Test discard confirmation modal appears
- [ ] **Testing: E2E Tests** (AC: 4.4, 4.5, 4.6, 4.7)
  - [ ] E2E-4.2: Login as BPO, navigate to pending reviews, approve a suggestion, verify active record created
  - [ ] E2E-4.3: Login as BPO, edit a suggestion, approve, verify active record has edited values
  - [ ] E2E-4.4: Login as BPO, discard a suggestion, verify status updated to "archived"
  - [ ] Test non-BPO user cannot access `/dashboard/bpo/reviews` (403 error)

## Dev Notes

### Architecture Patterns

- **Service Layer Pattern**: Centralize assessment logic in `AssessmentService` to keep endpoints thin and testable (following AuditService pattern from Story 3.4)
- **Audit Integration**: Use `AuditService.log_action()` from Story 3.4 for all assessment actions (approve, edit, discard)
- **Atomic Transactions**: Use database transactions to ensure consistency - if audit logging fails, rollback entire assessment action
- **Authorization Strategy**: Multi-layer checks - JWT validation, BPO role check, assigned_bpo_id match, tenant isolation via RLS
- **Optimistic Locking**: Validate suggestion status is still "pending_review" before processing to prevent race conditions
- **Form State Management**: Use React Hook Form for review detail form with inline editing toggle

### Source Tree Components

**New Files:**
- `backend/app/schemas/assessment.py` - Pydantic schemas for assessment request/response
- `backend/app/services/assessment_service.py` - Assessment business logic (approve, discard)
- `backend/app/api/v1/endpoints/assessments.py` - Assessment API endpoints
- `frontend/app/(dashboard)/bpo/reviews/page.tsx` - Pending reviews list page
- `frontend/app/(dashboard)/bpo/reviews/[id]/page.tsx` - Review detail page

**Modified Files:**
- `backend/app/main.py` - Register assessments router
- `frontend/app/(dashboard)/page.tsx` - Add "Pending Reviews" card for BPO role (from Story 4.1)

### Testing Standards

- **Backend Unit Tests**: Follow pattern from `backend/tests/services/test_audit_service.py` (Story 3.4)
- **Backend Integration Tests**: Test with real database, verify tenant isolation, authorization checks, and audit logging
- **Frontend Unit Tests**: Test components with React Testing Library, mock API calls
- **E2E Tests**: Use Playwright for end-to-end BPO assessment workflow
- **Coverage Target**: 80% code coverage for new services and components

### Project Structure Notes

**Alignment:**
- Backend follows standard structure: `backend/app/services/`, `backend/app/schemas/`, `backend/app/api/v1/endpoints/`
- Frontend follows Next.js App Router structure: `frontend/app/(dashboard)/bpo/reviews/`
- Consistent with architecture decisions from `docs/architecture.md`

**Conflicts:**
- None detected

### Learnings from Previous Story

**From Story 4-2-implement-real-time-status-updates (Status: ready-for-dev)**

- **New Files to be Created** (not yet implemented, but designed in Story 4.2):
  - `frontend/hooks/useRealtimeSubscription.ts` - Custom hook for Supabase Realtime subscriptions
  - `frontend/components/custom/RealtimeStatusIndicator.tsx` - Connection status badge component
- **Modified Files** (planned): `frontend/app/(dashboard)/page.tsx`, `frontend/app/(dashboard)/layout.tsx`
- **Patterns Established**: Custom hook pattern for Realtime, cache invalidation via queryClient.invalidateQueries()
- **Graceful Degradation**: 60-second polling fallback when Realtime disconnected
- **Tenant Isolation**: Realtime filters by tenant_id, enforced by RLS policies

**Relevance to This Story:**
- Story 4.3 (BPO assessment workflow) will need the dashboard components from Story 4.1
- BPO "Pending Reviews" interface will be a new route under dashboard
- Assessment actions (approve/edit/discard) will trigger Realtime updates (via Story 4.2's hook) when they modify database records
- Will integrate with AuditService from Story 3.4 to log all assessment actions
- Must follow authorization patterns: JWT validation, role checks, tenant isolation

[Source: docs/sprint-artifacts/4-2-implement-real-time-status-updates.md#Dev-Agent-Record]

**From Story 3-4-implement-immutable-audit-trail (Status: done)**

- **AuditService Available**: Use `backend/app/services/audit_service.py` - call `log_action(db, actor_id, action, entity_type, entity_id, changes)` method
- **Integration Pattern**: AuditService integrated into `update_suggestion_status` endpoint (suggestions.py)
- **JSON Diff for Edits**: AuditService calculates JSON diff between old and new values for UPDATE actions
- **Audit Log Retrieval**: `GET /api/v1/audit-logs` endpoint available for viewing audit trail

**Relevance to This Story:**
- AssessmentService MUST integrate with AuditService to log approve, edit, discard actions
- For "edit then approve" flow, use JSON diff to show original vs. edited values in audit log
- Ensure atomic transactions: if `AuditService.log_action()` fails, rollback assessment

[Source: docs/sprint-artifacts/3-4-implement-immutable-audit-trail.md#Dev-Agent-Record]

### References

- [Tech Spec: Epic 4](docs/sprint-artifacts/tech-spec-epic-4.md#Services-and-Modules) - AssessmentService, BPOReviewInterface specifications
- [Tech Spec: Epic 4](docs/sprint-artifacts/tech-spec-epic-4.md#Data-Models-and-Contracts) - AssessmentRequest, AssessmentResponse Pydantic schemas
- [Tech Spec: Epic 4](docs/sprint-artifacts/tech-spec-epic-4.md#APIs-and-Interfaces) - BPO Pending Reviews List, Submit BPO Assessment endpoints
- [Tech Spec: Epic 4](docs/sprint-artifacts/tech-spec-epic-4.md#Workflows-and-Sequencing) - Workflow 2 (Approve), Workflow 3 (Edit then Approve), Workflow 4 (Discard)
- [Tech Spec: Epic 4](docs/sprint-artifacts/tech-spec-epic-4.md#NFR-Security) - Authorization requirements (JWT, role check, assigned_bpo_id validation)
- [Tech Spec: Epic 4](docs/sprint-artifacts/tech-spec-epic-4.md#Dependencies-and-Integrations) - Audit Logging Service integration
- [Architecture](docs/architecture.md#Service-Layer-Pattern) - Service layer pattern for business logic
- [Epics](docs/epics.md#Story-4-3) - Original story definition from epic breakdown

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

### Completion Notes List

### File List
