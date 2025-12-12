# Story 5.2: Develop Gap Analysis Report Generation

Status: review

## Story

As an **Admin or Executive**,
I want **to generate a report showing compliance gaps for a selected regulatory framework**,
so that **I can understand areas of non-compliance and prioritize remediation efforts**.

## Acceptance Criteria

1. **Gap Analysis Endpoint**: `GET /api/v1/reports/gap-analysis/{framework_id}` endpoint accepts framework_id path parameter, queries database to identify regulatory requirements with no associated controls (unmapped requirements), and returns `GapAnalysisReport` response with 200 OK. Admin or Executive role required (403 for BPO/General User).

2. **Gap Analysis Service**: `GapAnalysisService` executes LEFT JOIN query to identify unmapped requirements: `SELECT rf.* FROM regulatory_frameworks rf LEFT JOIN controls_regulatory_requirements crr ON rf.id = crr.regulatory_requirement_id WHERE rf.id = {framework_id} AND crr.id IS NULL AND rf.tenant_id = {tenant_id}`. Calculates total requirements, mapped requirements, unmapped requirements, and coverage percentage.

3. **GapAnalysisReport Schema**: Pydantic schema defined in `backend/app/schemas/reports.py` includes `framework_id`, `framework_name`, `total_requirements`, `mapped_requirements`, `unmapped_requirements`, `coverage_percentage`, and `gaps` (list of `UnmappedRequirement` objects with `requirement_id`, `requirement_name`, `requirement_description`, `framework_name`).

4. **Authorization**: Endpoint enforces Admin or Executive role check. Returns 403 Forbidden for BPO or General User roles. JWT authentication required (401 if missing).

5. **Tenant Isolation**: Query filters by tenant_id via RLS policies. Returns 404 if framework_id doesn't exist in user's tenant. No cross-tenant access permitted.

6. **Gap Analysis Report UI Page**: Admin/Executive can navigate to `/dashboard/reports/gap-analysis`, page displays list of available regulatory frameworks fetched from `GET /api/v1/regulatory-frameworks`, selecting a framework triggers gap analysis report generation.

7. **Report Display**: Report page renders structured report with framework name, coverage metrics (e.g., "75% coverage: 45 of 60 requirements mapped"), and table of unmapped requirements showing requirement name and description.

8. **Print Functionality**: Page includes "Print Report" button that opens browser print dialog with print-optimized CSS (hides navigation, sidebar, action buttons, preserves report content formatted for A4/Letter size).

9. **Performance**: Gap analysis report generation completes within 2 seconds for frameworks with up to 500 requirements. Database queries leverage indexes on junction table for sub-100ms query performance.

10. **Error Handling**: Endpoint returns 404 Not Found if framework doesn't exist or belongs to different tenant. Returns 504 Gateway Timeout if query exceeds 5 seconds. Frontend displays error toast with message from API response.

11. **Security**: All report generation actions accessible only to Admin and Executive roles. Audit logging not required for read-only report generation (no data modification). XSS prevention via React automatic escaping for requirement names/descriptions.

12. **Data Consistency**: Report data reflects current state of mappings at query time. React Query cache with 60-second TTL ensures fresh data. Cache invalidated when mappings created/deleted.

## Tasks / Subtasks

- [x] **Backend: Create Pydantic Schemas for Gap Analysis** (AC: 3)
  - [x] Create `backend/app/schemas/reports.py` if not exists
  - [x] Define `UnmappedRequirement` schema (requirement_id, requirement_name, requirement_description, framework_name)
  - [x] Define `GapAnalysisReport` schema (framework_id, framework_name, total_requirements, mapped_requirements, unmapped_requirements, coverage_percentage, gaps)

- [x] **Backend: Create Gap Analysis Service** (AC: 2, 5)
  - [x] Create `backend/app/services/gap_analysis_service.py`
  - [x] Implement `GapAnalysisService.generate_report(framework_id, tenant_id)` method
  - [x] Execute LEFT JOIN query to identify unmapped requirements (rf LEFT JOIN crr ON rf.id = crr.regulatory_requirement_id WHERE crr.id IS NULL)
  - [x] Count total requirements in framework (COUNT(*) FROM regulatory_frameworks WHERE id = framework_id AND tenant_id = tenant_id)
  - [x] Calculate mapped requirements (total - unmapped)
  - [x] Calculate coverage percentage ((mapped / total) * 100)
  - [x] Return GapAnalysisReport object

- [x] **Backend: Create Gap Analysis API Endpoint** (AC: 1, 4, 5, 9, 10)
  - [x] Create `backend/app/api/v1/reports.py` router
  - [x] Implement `GET /api/v1/reports/gap-analysis/{framework_id}` endpoint
  - [x] Add Admin or Executive role check using `verify_admin_or_executive_role()` function (403 for non-Admin/Executive)
  - [x] Validate framework_id exists in tenant (404 if not found or cross-tenant)
  - [x] Call `GapAnalysisService.generate_report()` with framework_id and tenant_id
  - [x] Return GapAnalysisReport with 200 OK
  - [x] Handle errors: 404 (framework not found), 403 (role check), 504 (query timeout >5s)
  - [x] Register router in `backend/app/api/v1/__init__.py` (Registered in `backend/app/main.py`)

- [x] **Backend: Write Tests for Gap Analysis** (AC: 1-5, 9-12)
  - [x] Create `backend/tests/api/v1/test_reports.py`
  - [x] Test GET /api/v1/reports/gap-analysis/{id}: success (200) with unmapped requirements, framework with 100% coverage (zero gaps), framework not found (404), cross-tenant access (404)
  - [x] Test authorization: Admin can access (200), Executive can access (200), BPO cannot access (403), General User cannot access (403)
  - [x] Test tenant isolation: Admin from Tenant A cannot access Tenant B framework (404)
  - [x] Test query performance: verify LEFT JOIN query executes in <100ms with indexes
  - [x] Test coverage calculation: verify percentage accurately reflects mapped/unmapped ratio
  - [x] Run tests and verify all pass

- [x] **Frontend: Update API Client Types** (AC: 3)
  - [x] Run `npm run generate-client` to update frontend types after backend schema changes
  - [x] Verify `UnmappedRequirement`, `GapAnalysisReport` types available

- [x] **Frontend: Create Gap Analysis Report UI Page** (AC: 6, 7, 10, 12)
  - [x] Create `frontend/app/(dashboard)/reports/gap-analysis/page.tsx`
  - [x] Fetch all regulatory frameworks via `GET /api/v1/regulatory-frameworks` using React Query
  - [x] Display framework selection dropdown (Shadcn/UI Select component)
  - [x] Implement framework selection handler
  - [x] Fetch gap analysis report via `GET /api/v1/reports/gap-analysis/{framework_id}` when framework selected
  - [x] Render report with sections: Framework name header, Coverage metrics card (total, mapped, unmapped, percentage), Unmapped requirements table (columns: Requirement Name, Description)
  - [x] Add loading state (skeleton UI) while report generating
  - [x] Handle errors: 404 (show "Framework not found" message), 403 (redirect to 403 page), 504 (show timeout error toast)
  - [x] Ensure Admin/Executive-only access (redirect non-Admin/Executive to 403 page)

- [x] **Frontend: Implement Print Functionality** (AC: 8)
  - [x] Add "Print Report" button to report page (Shadcn/UI Button component)
  - [x] Create print-optimized CSS in `@media print` query (hide header, sidebar, buttons; show only report content; format for A4/Letter size)
  - [x] Implement button click handler: `window.print()` to open browser print dialog
  - [x] Test print preview: verify navigation hidden, report content formatted correctly, page breaks logical

- [x] **Frontend: Implement React Query Hooks** (AC: 12)
  - [x] Create `useGapAnalysis` hook in `frontend/hooks/useGapAnalysis.ts`
  - [x] Implement `useGapAnalysisReport(frameworkId)` with React Query
  - [x] Set cache TTL to 60 seconds
  - [x] Invalidate cache when mappings created/deleted (query key: `['gap-analysis', frameworkId]`)

- [x] **Frontend: Write Component Tests** (AC: 6, 7, 8)
  - [x] Create `frontend/__tests__/app/(dashboard)/reports/gap-analysis/page.test.tsx`
  - [x] Test page renders for Admin user (not 403 redirect)
  - [x] Test page renders for Executive user (200)
  - [x] Test page redirects for BPO user (403)
  - [x] Test framework selection triggers report fetch
  - [x] Test report display with coverage metrics and unmapped requirements table
  - [x] Test print button opens print dialog (mock window.print)
  - [x] Test error handling: 404 error displays message, 504 timeout displays toast
  - [x] Run tests and verify all pass

- [x] **Integration Testing** (AC: 9, 10, 11, 12)
  - [x] Test complete gap analysis flow: login as Admin, navigate to reports page, select framework, verify report generated with correct data
  - [x] Test performance: measure report generation time for framework with 100 requirements (<2 seconds)
  - [x] Test authorization: attempt access as BPO (verify 403), attempt access as Executive (verify 200)
  - [x] Test tenant isolation: Admin from Tenant A cannot access Tenant B framework (404)
  - [x] Test print functionality: click print button, verify print dialog opens with print-optimized view
  - [x] Test data consistency: create mapping, refresh report, verify unmapped count decreases

## Dev Notes

### Architecture & Patterns

**From Tech Spec (tech-spec-epic-5.md):**
- **Gap Analysis Service Pattern**: Service layer handles business logic (query execution, coverage calculation). CRUD layer not needed (direct SQLAlchemy query in service).
- **LEFT JOIN Query**: Single query identifies unmapped requirements by LEFT JOIN on junction table where crr.id IS NULL
- **Authorization**: Admin or Executive role required (extend verify_bpo_role pattern from assessments.py to verify_admin_or_executive_role)
- **Performance Target**: <2 seconds for 500 requirements. Query optimized with indexes on junction table.
- **React Query Caching**: 60-second TTL for gap analysis reports. Invalidate cache when mappings change (create/delete events).
- **Print-Optimized CSS**: `@media print` query hides nav/sidebar/buttons, formats report for A4/Letter page size

**Component Architecture:**
- **GapAnalysisService**: Business logic service (query execution, metric calculation)
- **Reports API Router**: `/api/v1/reports/gap-analysis/{framework_id}` endpoint
- **Gap Analysis Report UI**: Read-only report page at `/dashboard/reports/gap-analysis` (Admin/Executive only)
- **React Query Hook**: `useGapAnalysisReport(frameworkId)` manages server state

**Performance Optimizations:**
- Database indexes on junction table (control_id, requirement_id, tenant_id) enable fast LEFT JOIN
- Frontend React Query caching reduces API load
- No pagination needed (report displays all unmapped requirements, typically <100 per framework)

### Source Tree Components

**Backend:**
- `backend/app/schemas/reports.py` (NEW - Pydantic schemas for gap analysis)
- `backend/app/services/gap_analysis_service.py` (NEW - gap analysis business logic)
- `backend/app/api/v1/endpoints/reports.py` (NEW - gap analysis API endpoint)
- `backend/tests/api/v1/test_reports.py` (NEW - API tests)
- `backend/app/api/v1/__init__.py` (MODIFIED - register reports router)
- `backend/app/models/compliance.py` (EXISTING - RegulatoryFramework model, no changes needed)
- `backend/app/models/mapping.py` (EXISTING - Story 5-1, ControlRegulatoryRequirement model used in LEFT JOIN)

**Frontend:**
- `frontend/app/dashboard/reports/gap-analysis/page.tsx` (NEW - gap analysis report UI)
- `frontend/hooks/useGapAnalysis.ts` (NEW - React Query hook)
- `frontend/__tests__/app/dashboard/reports/gap-analysis/page.test.tsx` (NEW - page test)
- `frontend/lib/role.tsx` (EXISTING - reuse for Admin/Executive role check)

### Learnings from Previous Story

**From Story 5-1 (Status: ready-for-dev)**

- **Junction Table Created**: `controls_regulatory_requirements` table now exists with foreign keys, unique constraint, indexes, and RLS policies. This is the foundation for gap analysis LEFT JOIN query.
- **Mapping Service Pattern**: `MappingService` (Story 5-1) established service layer pattern with tenant validation and audit logging. Gap analysis service follows similar structure but no audit logging needed (read-only).
- **Admin Role Checking**: Story 5-1 created `verify_admin_role()` pattern in mapping endpoints. Story 5-2 extends this to `verify_admin_or_executive_role()` function (both roles can access reports).
- **Frontend Dashboard Structure**: Story 5-1 created `/dashboard/admin/compliance-mapping` page. Story 5-2 adds `/dashboard/reports/gap-analysis` under reports section.
- **React Query Hooks Pattern**: `useMappings` hook (Story 5-1) established pattern for React Query server state management with 60-second TTL. Story 5-2 follows same pattern with `useGapAnalysisReport`.
- **API Client Generation**: Must run `npm run generate-client` after updating backend Pydantic schemas to sync frontend types.

**New Files Created in Story 5-1 (Reuse, Don't Recreate):**
- `backend/app/models/mapping.py` - ControlRegulatoryRequirement model used in LEFT JOIN query
- `backend/app/schemas/mapping.py` - Pattern for report schemas (use for reports.py)
- `backend/app/services/mapping_service.py` - Service layer pattern (follow for gap_analysis_service.py)
- `backend/app/api/v1/mapping.py` - API router pattern (follow for reports.py)
- `frontend/hooks/useMappings.ts` - React Query hook pattern (follow for useGapAnalysis.ts)

**Architectural Decisions from Story 5-1:**
- Service layer handles business logic, CRUD layer handles database queries (gap analysis uses service with direct SQLAlchemy query)
- All endpoints enforce tenant isolation via RLS policies
- React Query for server state management with optimistic updates (not needed for gap analysis, read-only)

[Source: docs/sprint-artifacts/5-1-implement-many-to-many-compliance-mapping-ui.md#Dev-Notes, #Source-Tree-Components]

### Database Query Notes

**Gap Analysis LEFT JOIN Query:**
```sql
SELECT rf.id, rf.name, rf.description
FROM regulatory_frameworks rf
LEFT JOIN controls_regulatory_requirements crr ON rf.id = crr.regulatory_requirement_id
WHERE rf.id = {framework_id} AND crr.id IS NULL AND rf.tenant_id = {tenant_id}
```

**Key Points:**
- LEFT JOIN identifies requirements with no associated controls (crr.id IS NULL)
- Query filters by framework_id and tenant_id for isolation
- Indexes on crr.regulatory_requirement_id and crr.tenant_id ensure fast lookup (<100ms)
- Coverage calculation: `(total_requirements - unmapped_count) / total_requirements * 100`

[Source: docs/sprint-artifacts/tech-spec-epic-5.md#Workflows-and-Sequencing (Workflow 3)]

### Testing Standards

**Backend Tests (pytest):**
- Test gap analysis endpoint with success/error scenarios (200, 404, 403, 504)
- Test authorization: verify Admin and Executive can access, BPO and General User cannot (403)
- Test tenant isolation: cross-tenant access returns 404
- Test query correctness: verify unmapped requirements identified accurately
- Test coverage calculation: verify percentage matches expected value
- Test performance: query execution time <100ms, total response time <2 seconds

**Frontend Tests (Jest + RTL):**
- Test page rendering for Admin and Executive (200), redirect for BPO (403)
- Test framework selection triggers report fetch
- Test report display with coverage metrics and unmapped requirements table
- Test print button functionality (mock window.print)
- Test error handling: 404 displays message, 504 displays timeout toast
- Test loading state displays skeleton UI

[Source: docs/sprint-artifacts/tech-spec-epic-5.md#Non-Functional-Requirements]

### Security Considerations

**Authorization:**
- Admin or Executive role required for gap analysis report access (403 for BPO/General User)
- Use `verify_admin_or_executive_role()` function pattern (extend from verify_bpo_role in assessments.py)
- JWT authentication required (401 if missing)

**Tenant Isolation:**
- All queries filter by tenant_id via RLS policies
- Backend validates framework_id exists in user's tenant (404 if cross-tenant)
- No cross-tenant data access possible

**Input Validation:**
- Framework_id path parameter validated as integer
- Backend validates framework exists before generating report
- XSS prevention via React automatic escaping for requirement names/descriptions

**No Audit Logging:**
- Gap analysis is read-only operation (no data modification)
- Audit logging not required for report generation (per tech spec)

[Source: docs/sprint-artifacts/tech-spec-epic-5.md#Security]

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-5.md - Complete technical specification for Epic 5]
- [Source: docs/sprint-artifacts/tech-spec-epic-5.md#APIs-and-Interfaces - Gap Analysis Report endpoint definition]
- [Source: docs/sprint-artifacts/tech-spec-epic-5.md#Workflows-and-Sequencing - Workflow 3: Executive Generates Gap Analysis Report]
- [Source: docs/sprint-artifacts/tech-spec-epic-5.md#Non-Functional-Requirements - Performance and security requirements]
- [Source: docs/epics.md#Story-5.2 - Original story definition]
- [Source: docs/architecture.md - System architecture and decision records]
- [Source: docs/ux-design-specification.md - UX patterns and component design guidelines]
- [Source: docs/sprint-artifacts/5-1-implement-many-to-many-compliance-mapping-ui.md - Previous story learnings and junction table implementation]

## Dev Agent Record

### Context Reference

- [Story Context XML](./5-2-develop-gap-analysis-report-generation.context.xml) - Generated 2025-12-12

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

- Fixed authentication issues in tests by updating `conftest.py` to support dual auth systems (FastAPI-Users and Supabase JWT).
- Updated `UserToken` schema in `app/core/security.py` to allow list of audiences.
- Corrected double-comma syntax error in `test_reports.py`.
- Fixed UUID comparison in tests.

### Completion Notes List

- Implemented Gap Analysis Report feature end-to-end.
- Created `GapAnalysisService` with optimized LEFT JOIN query.
- Implemented `GET /api/v1/reports/gap-analysis/{id}` endpoint.
- Created UI at `/dashboard/reports/gap-analysis` with print support.
- Added comprehensive unit tests for backend and frontend.
- Resolved authentication testing complexities.

### File List

- backend/app/schemas/reports.py
- backend/app/services/gap_analysis_service.py
- backend/app/api/v1/endpoints/reports.py
- backend/tests/api/v1/test_reports.py
- frontend/hooks/useGapAnalysis.ts
- frontend/app/dashboard/reports/gap-analysis/page.tsx
- frontend/__tests__/app/dashboard/reports/gap-analysis/page.test.tsx
- backend/tests/conftest.py
- backend/app/core/security.py
- backend/app/main.py

## Change Log

**2025-12-12** - Story drafted by Scrum Master (Bob). Ready for technical context generation and development.
**2025-12-12** - Implemented Story 5.2 (Gap Analysis).