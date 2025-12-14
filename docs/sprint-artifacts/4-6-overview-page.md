# Story 4.6: Overview Page

Status: ready-for-dev

## Story

As a **user**,
I want **to view all accepted risks, controls, and business processes in a unified hierarchical overview page**,
so that **I can see the complete compliance framework in one place with processes as parent items linking to their associated controls and risks**.

## Acceptance Criteria

1. **Navigation & Access**
   - Given I am any authenticated user,
   - When I navigate to `/dashboard/overview`,
   - Then the page loads and displays all accepted compliance items.

2. **Dashboard Card**
   - Given I am on the dashboard,
   - When I view dashboard cards,
   - Then I see an "Overview" card showing the total count of accepted items (risks + controls + processes) with a "View" button.
   - And clicking "View" navigates to `/dashboard/overview`.

3. **Hierarchical Tree View**
   - Given I am on the Overview page,
   - When I view the content,
   - Then I see an expandable tree structure with processes as parent nodes.
   - And each process expands to show its associated controls and risks as child nodes.
   - And tree nodes can be collapsed/expanded independently.

4. **Tabbed Views**
   - Given I am on the Overview page,
   - When I want to filter by entity type,
   - Then I can toggle between tabs: "All" (tree view), "Processes", "Controls", "Risks".
   - And each tab shows the relevant filtered list.

5. **Admin Edit/Delete (Modal)**
   - Given I am logged in as Admin,
   - When I click "Edit" on any item in the tree,
   - Then a modal dialog opens with the item's editable form pre-populated.
   - And I can save changes or cancel without leaving the page.
   - And clicking "Delete" shows a confirmation modal before deletion.

6. **Read-Only for Non-Admin**
   - Given I am logged in as a non-Admin user (BPO, Executive, General User),
   - When I view the Overview page,
   - Then I can see all items but cannot edit or delete them (no action buttons visible).

## Tasks / Subtasks

- [ ] **Backend: Update Dashboard Metrics** (AC: #2)
  - [ ] Modify `backend/app/services/dashboard_service.py` to replace "System Health" card with "Overview" card
  - [ ] Update metric calculation to include processes count: `total_risks + total_controls + total_processes`
  - [ ] Change `action_link` from `/dashboard/admin/system` to `/dashboard/overview`
  - [ ] Update `card_id` to "overview" and title to "Overview"

- [ ] **Backend: Create Overview API Endpoint** (AC: #1, #3, #6)
  - [ ] Create `GET /api/v1/dashboard/overview` endpoint in `backend/app/api/v1/endpoints/`
  - [ ] Fetch all accepted Controls, Risks, and BusinessProcesses for current tenant
  - [ ] Include relationship data (process → controls/risks mappings)
  - [ ] Return hierarchical JSON structure with processes as parents
  - [ ] Apply RLS (tenant filtering) and RBAC (all authenticated users can read)

- [ ] **Frontend: Create Overview Page Component** (AC: #1, #3, #4, #5, #6)
  - [ ] Create `frontend/app/dashboard/overview/page.tsx`
  - [ ] Implement data fetching using React Query from `/api/v1/dashboard/overview`
  - [ ] Build tree component (using Shadcn/UI Collapsible or custom tree)
  - [ ] Implement tabbed interface (All | Processes | Controls | Risks)
  - [ ] Add expand/collapse functionality for tree nodes
  - [ ] Show appropriate icons for each entity type (process, control, risk)

- [ ] **Frontend: Implement Modal Edit/Delete** (AC: #5)
  - [ ] Create reusable edit modal component accepting entity type and data
  - [ ] Load appropriate form based on entity type (Control/Risk/BusinessProcess)
  - [ ] Implement inline form submission with optimistic updates
  - [ ] Create delete confirmation modal with entity name display
  - [ ] Handle success/error states with toast notifications

- [ ] **Frontend: Role-Based UI Rendering** (AC: #5, #6)
  - [ ] Use `useRole()` hook to check if current user is Admin
  - [ ] Conditionally render Edit/Delete buttons only for Admin
  - [ ] Ensure read-only view for BPO, Executive, General User roles

- [ ] **Update Routing & Navigation** (AC: #1, #2)
  - [ ] Verify `/dashboard/overview` route is accessible
  - [ ] Update Dashboard card click handler to navigate to `/dashboard/overview`

- [ ] **Testing** (All ACs)
  - [ ] Backend: Test overview API endpoint with multiple tenants (RLS verification)
  - [ ] Backend: Test hierarchical data structure includes all relationships
  - [ ] Frontend: Test tree expand/collapse functionality
  - [ ] Frontend: Test tab switching behavior
  - [ ] Frontend: Test modal edit/delete flows (Admin only)
  - [ ] E2E: Test complete flow from dashboard card click → overview page → edit item

## Dev Notes

### Architecture Patterns

**Data Model:**
- Accepted items are those created from approved suggestions (moved from AI Review to main tables)
- Hierarchical relationship: `business_processes` (parent) → `controls`/`risks` (children)
- Use existing foreign key relationships: `controls.process_id` and `risks.process_id`

**Backend:**
- Endpoint: `GET /api/v1/dashboard/overview` (new)
- Service: Update `dashboard_service.py` for Overview card
- Auth: JWT from Supabase (existing pattern)
- RLS: Tenant filtering via `tenant_id` (existing pattern from other endpoints)

**Frontend:**
- Page: `frontend/app/dashboard/overview/page.tsx` (new)
- Components: Shadcn/UI Collapsible, Dialog (modal), Tabs
- Data fetching: React Query with `useQuery`
- Role check: `useRole()` hook (from `frontend/lib/role.ts`)

**Styling:**
- Follow existing Shadcn/UI theme and patterns
- Tree nodes: indented with expand/collapse icons
- Modals: centered overlay with backdrop dim

### Project Structure Notes

**Files to Create:**
- `frontend/app/dashboard/overview/page.tsx` - Main overview page component
- `frontend/app/dashboard/overview/components/OverviewTree.tsx` (optional) - Tree component
- `frontend/app/dashboard/overview/components/EditModal.tsx` (optional) - Edit modal
- `backend/app/api/v1/endpoints/overview.py` - New endpoint file OR add to existing dashboard.py

**Files to Modify:**
- `backend/app/services/dashboard_service.py` - Update Admin cards (replace "System Health" with "Overview")
- `backend/app/api/v1/api.py` - Add overview endpoint to router (if new file created)

**Existing Patterns to Reuse:**
- Modal patterns: See `frontend/components/delete-entity-button.tsx` for delete confirmation
- Form patterns: See existing edit pages like `frontend/app/dashboard/controls/[id]/edit/page.tsx`
- API client: Use OpenAPI-generated client from `frontend/app/clientService.ts`
- Authentication: Supabase JWT pattern from `frontend/lib/supabase.ts`

### Learnings from Previous Story (4-5)

**From Story 4-5-defect-controls-visibility (Status: done)**

- **Critical Field**: Ensure all entities have `owner_id` and `tenant_id` properly set
  - Previous defect: Controls created from suggestions were missing `owner_id`, breaking visibility
  - Fix location: `backend/app/api/v1/endpoints/suggestions.py:165`
  - **Action for this story**: Verify overview API query includes proper ownership and tenancy filters

- **RLS Policies**: Row-Level Security policies depend heavily on `owner_id` and `tenant_id`
  - If overview page shows unexpected results (missing items), check RLS policies first
  - Supabase RLS is applied automatically on queries

- **Testing Pattern**: Previous story added `backend/tests/api/v1/test_suggestion_approval.py`
  - Use similar integration test pattern for overview endpoint
  - Test multi-tenant scenarios to verify RLS isolation

- **Files Modified in Previous Story**:
  - `backend/app/api/v1/endpoints/suggestions.py` - Suggestion approval logic
  - `backend/tests/api/v1/test_suggestion_approval.py` - New test file
  - `backend/tests/api/v1/test_suggestions.py` - Updated mocks

[Source: docs/sprint-artifacts/4-5-defect-controls-visibility.md#Dev-Agent-Record]

### References

- [PRD - Core Data Management](../PRD.md#mvp---minimum-viable-product) - CRUD capabilities for risk matrix, risk register, control library
- [PRD - Basic Dashboard](../PRD.md#mvp---minimum-viable-product) - High-level overview of risk posture
- [Architecture - Data Persistence](../architecture.md#41-data-persistence) - Supabase PostgreSQL with RLS
- [Architecture - Real-time Updates](../architecture.md#44-real-time-updates) - Supabase Realtime for live updates (optional enhancement)
- [Epic 4 - Story 4.1](../epics.md#story-41-develop-role-specific-dashboards) - Dashboard card patterns
- [Epic 3 - Story 3.3](../epics.md#story-33-build-human-in-the-loop-hitl-validation-interface) - Two-panel layout pattern (reference for tree view)

## Dev Agent Record

### Context Reference

- docs/sprint-artifacts/4-6-overview-page.context.xml

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
