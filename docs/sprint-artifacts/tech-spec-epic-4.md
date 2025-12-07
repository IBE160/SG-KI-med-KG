# Epic Technical Specification: Real-Time Risk Monitoring & Assessment

Date: 2025-12-07
Author: BIP
Epic ID: 4
Status: Draft

---

## Overview

Epic 4 delivers the **Real-Time Risk Monitoring & Assessment** capability, transforming the ibe160 platform from a static data repository into a dynamic, action-oriented command center for compliance professionals. This epic provides role-specific dashboards that serve as personalized "Action-Oriented Hubs," real-time status updates via Supabase Realtime, and a streamlined control assessment workflow for Business Process Owners (BPOs). It directly addresses FR-6 (Role-Specific Dashboards), FR-7 (Real-Time Status Updates), and FR-9 (Streamlined Control Assessment).

The epic builds on the foundational data model (Epic 1), authentication and RBAC (Epic 2), and the AI-powered suggestion generation and HITL validation workflows (Epic 3). It transforms these underlying capabilities into an intuitive, real-time user experience that empowers users to monitor, assess, and act on compliance data with unprecedented efficiency.

## Objectives and Scope

**In Scope:**
- Design and implement role-specific dashboard layouts for Admin, BPO, Executive, and General User roles
- Create a modular, card-based "Action-Oriented Hub" dashboard using Shadcn/UI components
- Integrate Supabase Realtime for live updates of control/risk statuses across all dashboards
- Build a dedicated BPO "Pending Reviews" interface for acting on AI-promoted suggestions
- Implement the complete BPO assessment workflow: approve, edit (with change log), or discard items
- Enforce mandatory residual risk categorization (low/medium/high) before BPO approval
- Ensure all assessment actions are logged to the immutable audit trail (Epic 3)
- Optimize dashboard performance (LCP < 2.5s target)

**Out of Scope:**
- Advanced data visualization features (deferred to post-MVP)
- Custom reporting or export functionality (covered in Epic 5)
- Mobile/tablet-optimized layouts (desktop-first for MVP)
- User-configurable dashboard customization (future enhancement)

## System Architecture Alignment

This epic aligns with the decoupled Next.js (frontend) + FastAPI (backend) + Supabase architecture:

- **Frontend (Next.js):** Dashboard components will live in `frontend/app/(dashboard)` with role-based conditional rendering. Custom hooks (`frontend/hooks`) will manage Supabase Realtime subscriptions for live data updates. The UI leverages Shadcn/UI components and the defined "Clarity Green" (light) and "Focused Slate" (dark) themes.

- **Backend (FastAPI):** New API endpoints in `backend/app/api/v1/` will provide role-specific data feeds for dashboards and handle BPO assessment actions (approve/edit/discard). The assessment service will integrate with the audit logging system from Epic 3.

- **Supabase:** Realtime subscriptions will push database changes (e.g., control status updates) directly to connected clients. Row-Level Security (RLS) ensures tenant isolation and role-based data access.

- **State Management:** React Query manages server state caching and mutations. Zustand stores minimal global state (e.g., current user profile, theme preference).

- **Performance:** Dashboard cards use optimistic updates and skeleton loading states to minimize perceived latency.

## Detailed Design

### Services and Modules

| Module/Service | Location | Responsibilities | Inputs | Outputs | Owner |
|---|---|---|---|---|---|
| **DashboardService** | `backend/app/services/dashboard_service.py` | Aggregates role-specific metrics and data feeds for dashboard cards | `user_id`, `tenant_id`, `role` | JSON payload with metrics (pending reviews count, high-priority risks, etc.) | Backend Dev |
| **AssessmentService** | `backend/app/services/assessment_service.py` | Handles BPO assessment actions (approve/edit/discard), triggers audit logging | `suggestion_id`, `action` (approve/edit/discard), `residual_risk`, `edits` | Updated suggestion status, audit log entry | Backend Dev |
| **RealtimeSubscriptionHook** | `frontend/hooks/useRealtimeSubscription.ts` | Custom React hook to subscribe to Supabase Realtime channels for live updates | `table_name`, `filter_criteria` | Real-time data stream from Supabase | Frontend Dev |
| **DashboardLayout** | `frontend/app/(dashboard)/layout.tsx` | Provides consistent dashboard shell (sidebar, header, theme toggle) for all role views | User session data | Rendered layout with role-based navigation | Frontend Dev |
| **ActionCardComponent** | `frontend/components/custom/ActionCard.tsx` | Reusable modular card component for dashboard "Action-Oriented Hub" | `title`, `metric`, `action_link`, `icon` | Rendered card with CTA button | Frontend Dev |
| **BPOReviewInterface** | `frontend/app/(dashboard)/bpo/reviews/page.tsx` | Dedicated page for BPO pending reviews list and detail view | `bpo_id`, `pending_suggestions` | Interactive review interface | Frontend Dev |

### Data Models and Contracts

**Dashboard Metrics Response (Backend → Frontend)**

```python
# backend/app/schemas/dashboard.py
from pydantic import BaseModel
from typing import List, Optional

class DashboardCard(BaseModel):
    """Single card data for Action-Oriented Hub"""
    card_id: str  # e.g., "pending_reviews", "high_priority_risks"
    title: str
    metric: int  # Primary number to display
    metric_label: str  # e.g., "items", "risks"
    icon: str  # Icon identifier for frontend
    action_link: str  # URL for "View" CTA
    status: Optional[str] = None  # e.g., "urgent", "normal"

class DashboardMetrics(BaseModel):
    """Complete dashboard data feed for a user"""
    user_role: str  # "admin", "bpo", "executive", "general"
    cards: List[DashboardCard]
```

**BPO Assessment Request (Frontend → Backend)**

```python
# backend/app/schemas/assessment.py
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class ResidualRisk(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class AssessmentAction(str, Enum):
    approve = "approve"
    edit = "edit"
    discard = "discard"

class AssessmentRequest(BaseModel):
    """Payload for BPO assessment action"""
    suggestion_id: int
    action: AssessmentAction
    residual_risk: Optional[ResidualRisk] = Field(None, description="Required for 'approve' action")
    # Edits (optional for 'edit' action)
    edited_risk_description: Optional[str] = None
    edited_control_description: Optional[str] = None
    edited_business_process: Optional[str] = None

class AssessmentResponse(BaseModel):
    """Response after assessment action"""
    success: bool
    message: str
    updated_status: str  # "active", "archived", etc.
    audit_log_id: int  # Reference to audit trail entry
```

**Realtime Subscription Payload (Supabase → Frontend)**

```typescript
// frontend/types/realtime.ts
interface RealtimeChange {
  table: string;
  eventType: 'INSERT' | 'UPDATE' | 'DELETE';
  new: Record<string, any>;  // New row data
  old: Record<string, any>;  // Old row data (for UPDATE/DELETE)
}
```

### APIs and Interfaces

**Dashboard Data Endpoint**

- **Method:** `GET`
- **Path:** `/api/v1/dashboard/metrics`
- **Auth:** Required (JWT)
- **Query Params:** None (user derived from JWT)
- **Response:** `DashboardMetrics` (200 OK)
- **Error:** `401 Unauthorized`, `403 Forbidden`
- **Description:** Returns role-specific dashboard card data based on authenticated user

**BPO Pending Reviews List**

- **Method:** `GET`
- **Path:** `/api/v1/assessments/pending`
- **Auth:** Required (BPO role)
- **Query Params:** `?page=1&size=20` (pagination)
- **Response:** Paginated list of suggestions with status "pending_review" (200 OK)
- **Error:** `401 Unauthorized`, `403 Forbidden` (non-BPO users)

**Submit BPO Assessment**

- **Method:** `POST`
- **Path:** `/api/v1/assessments/{suggestion_id}/assess`
- **Auth:** Required (BPO role)
- **Request Body:** `AssessmentRequest`
- **Response:** `AssessmentResponse` (200 OK)
- **Error:**
  - `400 Bad Request` (missing residual_risk for approve action)
  - `404 Not Found` (suggestion doesn't exist or not assigned to this BPO)
  - `403 Forbidden` (user not BPO or not assigned to this suggestion)
- **Side Effects:**
  - Updates suggestion status in database
  - Creates audit log entry
  - If approved, creates active risk/control records

### Workflows and Sequencing

**Workflow 1: Dashboard Load & Real-Time Updates**

1. User navigates to `/dashboard`
2. Frontend calls `GET /api/v1/dashboard/metrics` with JWT
3. Backend DashboardService queries database for user's role and tenant
4. Backend aggregates metrics (e.g., count of pending reviews, high-priority risks)
5. Backend returns `DashboardMetrics` JSON
6. Frontend renders role-specific dashboard cards
7. Frontend establishes Supabase Realtime subscription to `controls` and `risks` tables (filtered by tenant)
8. When database changes occur (e.g., BPO approves a control), Supabase pushes event to frontend
9. Frontend React Query cache invalidates and refetches metrics
10. Dashboard cards update without page refresh

**Workflow 2: BPO Assessment (Approve)**

1. BPO clicks "Pending Reviews" card → navigates to `/dashboard/bpo/reviews`
2. Frontend calls `GET /api/v1/assessments/pending`
3. BPO selects a suggestion from list → detail view loads
4. BPO reviews AI-suggested data, source reference, and editable fields
5. BPO selects residual risk (low/medium/high) from dropdown
6. BPO clicks "Approve"
7. Frontend sends `POST /api/v1/assessments/{id}/assess` with `action: approve`, `residual_risk: medium`
8. Backend AssessmentService validates request (checks residual_risk present)
9. Backend creates active risk/control/business_process records in database
10. Backend updates suggestion status to "active"
11. Backend creates audit log entry (who approved, when, residual risk value)
12. Backend returns success response with `audit_log_id`
13. Frontend displays toast: "✅ Successfully added to register" with link to view active item
14. Frontend returns BPO to pending reviews list (item removed from list)

**Workflow 3: BPO Assessment (Edit then Approve)**

1. BPO opens suggestion detail view
2. BPO clicks "Edit" button
3. Form fields become editable inline
4. BPO modifies risk description, control description, or business process
5. Frontend tracks all edits in local state
6. BPO selects residual risk and clicks "Approve"
7. Frontend sends `POST /api/v1/assessments/{id}/assess` with `action: approve`, `residual_risk: high`, `edited_risk_description: "Updated text..."`
8. Backend creates active records with edited values
9. Backend logs both approval AND edits to audit trail (change log shows original vs. edited)
10. Frontend confirms success

**Workflow 4: BPO Assessment (Discard)**

1. BPO opens suggestion detail view
2. BPO clicks "Discard"
3. Frontend shows confirmation modal: "Are you sure? This will archive the suggestion."
4. BPO confirms
5. Frontend sends `POST /api/v1/assessments/{id}/assess` with `action: discard`
6. Backend updates suggestion status to "archived"
7. Backend creates audit log entry (discard action)
8. Backend returns success
9. Frontend displays toast: "🗑️ Item discarded"
10. BPO returns to pending reviews list

## Non-Functional Requirements

### Performance

- **Dashboard Load Time:** Initial dashboard page load (LCP - Largest Contentful Paint) must be < 2.5 seconds on a standard broadband connection (as specified in UX requirements)
- **API Response Time:** Dashboard metrics endpoint (`GET /api/v1/dashboard/metrics`) must respond within 500ms under normal load
- **Real-Time Latency:** Supabase Realtime updates must reflect database changes on client dashboards within 1 minute (as specified in FR-7)
- **Concurrent Users:** System must support at least 50 concurrent authenticated users per tenant without performance degradation
- **Card Rendering:** Dashboard cards must use skeleton loading states to render instantly, with data populating asynchronously
- **Optimistic Updates:** BPO assessment actions should provide immediate UI feedback (optimistic updates) while backend processes the request

**Performance Targets (from Architecture):**
- Vercel (frontend) provides edge caching and CDN distribution for sub-200ms static asset delivery
- Railway (backend) must be configured with sufficient resources to handle dashboard aggregation queries efficiently
- React Query cache TTL for dashboard metrics: 30 seconds (balances freshness with API load)

### Security

- **Authentication:** All dashboard and assessment endpoints require valid JWT token in `Authorization: Bearer <token>` header
- **Role-Based Authorization:**
  - Dashboard metrics filtered by user role (Admin sees admin cards, BPO sees BPO cards, etc.)
  - BPO assessment endpoints (`/api/v1/assessments/*`) enforce BPO role check; return 403 if non-BPO attempts access
  - BPOs can only assess suggestions assigned to them (verified via `assigned_bpo_id` field)
- **Tenant Isolation:** All database queries enforce Row-Level Security (RLS) on `tenant_id` to prevent cross-tenant data access
- **Input Validation:** All assessment request payloads validated via Pydantic schemas; reject malformed requests with 400 Bad Request
- **Audit Logging:** All assessment actions (approve/edit/discard) logged to immutable audit trail with user identity, timestamp, and action details
- **XSS Prevention:** All user-generated content (edited descriptions, business process names) sanitized before rendering in frontend

### Reliability/Availability

- **Service Uptime:** Dashboard endpoints must maintain 99.5% uptime (consistent with Vercel/Railway SLA targets)
- **Graceful Degradation:** If Supabase Realtime is unavailable, dashboard falls back to periodic polling (every 60 seconds) to maintain some level of live updates
- **Error Handling:**
  - If dashboard metrics endpoint fails, frontend displays cached data (if available) with a warning banner: "Live data unavailable, showing last known state"
  - If BPO assessment action fails (network error, backend error), frontend displays clear error toast and does NOT optimistically update UI
- **Data Consistency:** BPO assessment actions (approve/discard) are atomic transactions; if audit logging fails, the entire transaction rolls back
- **Idempotency:** Assessment endpoint supports idempotent retries (duplicate approve requests return success without creating duplicate records)

### Observability

- **Backend Logging:**
  - All dashboard metrics queries logged with `user_id`, `tenant_id`, `role`, query duration
  - All assessment actions logged with `suggestion_id`, `action`, `bpo_id`, `result` (success/failure), duration
  - Errors logged with full stack trace and request context
- **Frontend Monitoring:**
  - Web vitals (LCP, FID, CLS) tracked and reported for dashboard page
  - API call failures logged to frontend error tracking (e.g., Sentry integration if available)
  - Supabase Realtime connection status monitored (connected/disconnected/reconnecting)
- **Metrics:**
  - Track count of dashboard loads per role per day
  - Track BPO assessment action distribution (approve vs. edit vs. discard) per tenant
  - Track average time-to-assessment (time from suggestion promotion to BPO action)
- **Alerts:**
  - Alert if dashboard metrics endpoint p95 latency exceeds 1 second
  - Alert if Supabase Realtime subscription failure rate exceeds 5%
  - Alert if BPO assessment endpoint error rate exceeds 2%

## Dependencies and Integrations

**External Dependencies (from pyproject.toml & Architecture):**

| Dependency | Version | Purpose | Integration Point |
|---|---|---|---|
| `@supabase/supabase-js` | v2.86.0 | Supabase client for Realtime subscriptions and auth | Frontend: `frontend/lib/supabase.ts`, used in `useRealtimeSubscription` hook |
| `@tanstack/react-query` | Latest stable | Server state management, caching, mutations | Frontend: Wraps all API calls, manages dashboard metrics cache |
| `zustand` | Latest stable | Minimal global state (user profile, theme) | Frontend: `frontend/stores/userStore.ts`, `frontend/stores/themeStore.ts` |
| Shadcn/UI | v0.8.0+ | Component library (Button, Card, Table, Toast, etc.) | Frontend: `frontend/components/ui/`, customized in `frontend/components/custom/` |
| FastAPI | v0.115.0 | Backend API framework | Backend: All endpoints in `backend/app/api/v1/` |
| Pydantic | v2.5.2+ | Request/response validation, schemas | Backend: `backend/app/schemas/dashboard.py`, `backend/app/schemas/assessment.py` |
| SQLAlchemy | (via fastapi-users) | ORM for database queries | Backend: `backend/app/models/`, `backend/app/crud/` |
| PostgreSQL (via Supabase) | v15+ | Primary database | Backend: All queries via SQLAlchemy; RLS policies enforce tenant isolation |

**Internal Module Dependencies:**

- **Epic 1 (Foundational Setup):** Dashboard queries the core data tables (`business_processes`, `risks`, `controls`, `regulatory_frameworks`) created in Epic 1
- **Epic 2 (IAM):** Dashboard and assessment endpoints rely on authentication (JWT) and RBAC (user roles) from Epic 2
- **Epic 3 (AI & Auditing):**
  - BPO assessment workflow acts on `ai_suggestions` table created in Epic 3
  - Assessment actions trigger audit log entries via Epic 3's audit logging service
  - "Pending Reviews" list displays suggestions with status "pending_review" (set by CO in Epic 3's HITL workflow)

**Integration Points:**

1. **Supabase Realtime:**
   - Frontend subscribes to `controls`, `risks`, `business_processes` tables (filtered by `tenant_id`)
   - On INSERT/UPDATE/DELETE events, frontend invalidates React Query cache and refetches dashboard metrics
   - Connection managed via `useRealtimeSubscription` custom hook

2. **Audit Logging Service (Epic 3):**
   - `AssessmentService.approve()` calls `AuditLogService.log_action(action="approve", user_id=..., suggestion_id=..., details={...})`
   - Ensures all BPO assessment actions are permanently recorded

3. **Authentication (Epic 2):**
   - All API endpoints decorated with `@requires_auth` middleware (validates JWT)
   - User role extracted from JWT claims and used for authorization checks

**Downstream Consumers:**

- **Epic 5 (Compliance Mapping & Reporting):** Gap analysis reports may query active controls and risks created via BPO assessment workflow in this epic

## Acceptance Criteria (Authoritative)

**AC-4.1: Role-Specific Dashboard Layout**
1. When an authenticated user navigates to `/dashboard`, the dashboard renders with content customized to their role (Admin, BPO, Executive, General User)
2. Admin dashboard displays admin-specific cards (e.g., "System Health", "User Management", "Analyze New Document")
3. BPO dashboard displays BPO-specific cards (e.g., "Pending Reviews", "My Controls", "Overdue Assessments")
4. Executive dashboard displays executive-specific cards (e.g., "Risk Overview", "Compliance Status", "Recent Activity")
5. General User dashboard displays read-only informational cards appropriate to their limited permissions
6. All dashboards use the modular card layout defined in UX specification with grid responsiveness

**AC-4.2: Dashboard Performance**
1. Dashboard page achieves Largest Contentful Paint (LCP) < 2.5 seconds on standard broadband
2. Dashboard cards render immediately with skeleton loading states while data loads asynchronously
3. `GET /api/v1/dashboard/metrics` endpoint responds within 500ms under normal load
4. Dashboard supports at least 50 concurrent users per tenant without performance degradation

**AC-4.3: Real-Time Status Updates**
1. When a control or risk status is updated in the database, all connected dashboards reflect the change within 1 minute
2. Frontend successfully establishes Supabase Realtime subscription to `controls`, `risks`, and `business_processes` tables filtered by user's `tenant_id`
3. When a Realtime event is received, React Query cache is invalidated and dashboard metrics are refetched automatically
4. If Realtime connection fails, dashboard gracefully falls back to 60-second polling
5. Realtime connection status is visible in dashboard (connected/reconnecting indicator)

**AC-4.4: BPO Pending Reviews Interface**
1. BPO user can click "Pending Reviews" card and navigate to `/dashboard/bpo/reviews`
2. Pending reviews page displays paginated list of all suggestions with status "pending_review" assigned to the logged-in BPO
3. List prominently displays Business Process, Risk, and Control names for each suggestion
4. BPO can click on a suggestion to open detailed review screen
5. Detail screen displays all AI-suggested data (risk description, control description, business process, owner) in editable form fields
6. Detail screen displays persistent `source_reference` link to original document clause
7. Non-BPO users attempting to access `/dashboard/bpo/reviews` receive 403 Forbidden error

**AC-4.5: BPO Assessment - Approve Action**
1. BPO can select residual risk (low/medium/high) from dropdown on review detail screen
2. Residual risk selection is mandatory before "Approve" button is enabled
3. When BPO clicks "Approve", frontend sends `POST /api/v1/assessments/{id}/assess` with `action: approve` and `residual_risk`
4. Backend validates residual_risk is present; returns 400 Bad Request if missing
5. Backend creates active records in `business_processes`, `risks`, and `controls` tables with approved data
6. Backend updates suggestion status to "active"
7. Backend creates audit log entry with action="approve", user_id, suggestion_id, residual_risk, timestamp
8. Frontend displays success toast: "✅ Successfully added to register" with link to view active item
9. Suggestion is removed from pending reviews list

**AC-4.6: BPO Assessment - Edit Action**
1. BPO can click "Edit" button to enable inline editing of form fields
2. BPO can modify risk description, control description, and business process fields
3. Frontend tracks all edits in local state
4. When BPO approves after editing, frontend sends edited values in `AssessmentRequest` payload
5. Backend creates active records with edited values (not original AI-suggested values)
6. Audit log records both approval action AND field-level changes (original vs. edited values)
7. Change log is visible when viewing the active item

**AC-4.7: BPO Assessment - Discard Action**
1. BPO can click "Discard" button on review detail screen
2. Frontend displays confirmation modal: "Are you sure? This will archive the suggestion."
3. When BPO confirms, frontend sends `POST /api/v1/assessments/{id}/assess` with `action: discard`
4. Backend updates suggestion status to "archived"
5. Backend creates audit log entry with action="discard"
6. Frontend displays toast: "🗑️ Item discarded"
7. BPO returns to pending reviews list, discarded item removed

**AC-4.8: Authorization and Tenant Isolation**
1. All dashboard and assessment endpoints require valid JWT in Authorization header; return 401 if missing/invalid
2. BPO can only assess suggestions where `assigned_bpo_id` matches their user ID; return 403 otherwise
3. All database queries enforce Row-Level Security filtering by `tenant_id`
4. BPO from Tenant A cannot view or assess suggestions from Tenant B (404 returned)

**AC-4.9: Audit Trail Integration**
1. All BPO assessment actions (approve, edit, discard) create immutable audit log entry
2. Audit log includes: user_id, action, suggestion_id, timestamp, details (residual_risk, edits if any)
3. If audit logging fails, entire assessment transaction rolls back (data consistency)

## Traceability Mapping

| AC ID | Epic/Story | Spec Section | Component/API | Test Idea |
|---|---|---|---|---|
| AC-4.1 | Story 4.1 | Services: DashboardService, DashboardLayout | `GET /api/v1/dashboard/metrics`, `frontend/app/(dashboard)/layout.tsx` | Test: Login as each role, verify correct cards displayed |
| AC-4.2 | Story 4.1 | NFR: Performance | Dashboard metrics endpoint, ActionCard component | Test: Lighthouse audit, API response time measurement |
| AC-4.3 | Story 4.2 | Services: RealtimeSubscriptionHook, Workflows: Workflow 1 | Supabase Realtime, `useRealtimeSubscription` hook | Test: Update control status, verify dashboard updates within 1 min |
| AC-4.4 | Story 4.3 | Services: BPOReviewInterface | `GET /api/v1/assessments/pending`, `frontend/app/(dashboard)/bpo/reviews/page.tsx` | Test: Login as BPO, verify pending reviews list displays correctly |
| AC-4.5 | Story 4.3 | Data Models: AssessmentRequest, Workflows: Workflow 2 | `POST /api/v1/assessments/{id}/assess`, AssessmentService | Test: Approve suggestion, verify active records created, audit log entry exists |
| AC-4.6 | Story 4.3 | Data Models: AssessmentRequest (edited fields), Workflows: Workflow 3 | AssessmentService, inline editing UI | Test: Edit description, approve, verify active record has edited value, change log shows diff |
| AC-4.7 | Story 4.3 | Workflows: Workflow 4 | `POST /api/v1/assessments/{id}/assess` with action=discard | Test: Discard suggestion, verify status=archived, audit log entry created |
| AC-4.8 | All Stories | NFR: Security (Authorization, Tenant Isolation) | JWT middleware, RLS policies, AssessmentService authorization checks | Test: Attempt cross-tenant access, verify 403/404; attempt non-BPO access to BPO endpoint, verify 403 |
| AC-4.9 | Story 4.3 | Dependencies: Audit Logging Service (Epic 3) | AssessmentService → AuditLogService integration | Test: Simulate audit log failure, verify assessment transaction rolls back |

## Risks, Assumptions, Open Questions

**RISK-4.1: Supabase Realtime Performance at Scale**
- **Description:** Supabase Realtime may not reliably deliver updates within 1 minute when handling high volumes of concurrent subscriptions (e.g., 50+ users per tenant with multiple table subscriptions each)
- **Impact:** Dashboard updates may be delayed or missed, degrading user experience
- **Mitigation:** Implement fallback polling mechanism (every 60 seconds); load test Realtime subscriptions during development; consider batching database updates to reduce event volume; monitor Realtime connection metrics in production

**RISK-4.2: Dashboard Query Performance**
- **Description:** Dashboard metrics aggregation query may become slow as data volume grows (e.g., thousands of controls, risks, and suggestions per tenant)
- **Impact:** Exceeds 500ms API response time target, degrades dashboard load performance
- **Mitigation:** Add database indexes on frequently queried fields (`tenant_id`, `status`, `assigned_bpo_id`, `created_at`); implement query result caching with 30-second TTL; optimize SQL queries to use COUNT(*) instead of fetching full result sets; consider materialized views for complex metrics

**RISK-4.3: Race Conditions in BPO Assessment**
- **Description:** Multiple BPOs might attempt to assess the same suggestion simultaneously (if assignments are shared or misconfigured)
- **Impact:** Duplicate active records created, audit trail inconsistency
- **Mitigation:** Implement database-level optimistic locking on `ai_suggestions` table (version field); backend validates suggestion status is still "pending_review" before processing; use database transactions with SERIALIZABLE isolation level

**ASSUMPTION-4.1: BPO Assignment Logic Exists**
- **Assumption:** Epic 3 includes logic to assign `assigned_bpo_id` when CO promotes a suggestion to "pending_review"
- **Validation Required:** Verify Epic 3 implementation includes BPO assignment; if not, this epic must implement assignment logic

**ASSUMPTION-4.2: Single Active Record per Suggestion**
- **Assumption:** When BPO approves a suggestion, exactly one set of active records is created (one business_process, one risk, one control)
- **Validation Required:** Confirm with stakeholders if a single suggestion can create multiple controls or risks; adjust AssessmentService logic if needed

**ASSUMPTION-4.3: Residual Risk is Control-Specific**
- **Assumption:** Residual risk categorization applies to the control, not the risk or business process
- **Validation Required:** Verify with compliance experts where residual_risk field should be stored (controls table vs. risks table vs. separate assessment table)

**QUESTION-4.1: Dashboard Customization**
- **Question:** Will users be able to customize which cards appear on their dashboard, or is the layout fixed per role?
- **Impact:** If customizable, requires additional UI for card configuration and storage of user preferences
- **Decision Needed:** Out of scope for MVP (fixed layout per role); deferred to post-MVP enhancement

**QUESTION-4.2: Notification Delivery Method**
- **Question:** How should BPOs be notified when new items are in their "Pending Reviews" queue? (Email, in-app notification, or both?)
- **Impact:** Requires integration with notification service (SendGrid for email, or in-app notification system)
- **Decision Needed:** For MVP, rely on BPO checking dashboard manually; email notifications deferred to post-MVP

**QUESTION-4.3: Historical Dashboard Metrics**
- **Question:** Should dashboard display historical trends (e.g., "Risks resolved over time" chart) or only current state?
- **Impact:** Historical metrics require time-series data storage and visualization components
- **Decision Needed:** MVP displays current state only (snapshot metrics); historical trends deferred to Epic 5 or post-MVP

## Test Strategy Summary

**Unit Tests (Backend):**
- `DashboardService.get_metrics()`: Test role-based filtering, metric calculation accuracy, tenant isolation
- `AssessmentService.approve()`: Test active record creation, residual_risk validation, status update, audit logging
- `AssessmentService.discard()`: Test status update to "archived", audit logging
- Authorization middleware: Test JWT validation, role checks, tenant isolation

**Unit Tests (Frontend):**
- `useRealtimeSubscription` hook: Test subscription setup, event handling, cache invalidation
- `ActionCard` component: Test rendering with different props, click handlers
- Dashboard layout: Test role-based conditional rendering

**Integration Tests (Backend):**
- `POST /api/v1/assessments/{id}/assess` (approve): Test end-to-end flow from request to database records to audit log
- `POST /api/v1/assessments/{id}/assess` (discard): Test end-to-end flow
- `GET /api/v1/dashboard/metrics`: Test with real database, verify correct metrics for each role
- `GET /api/v1/assessments/pending`: Test pagination, filtering by assigned_bpo_id, tenant isolation

**Integration Tests (Frontend):**
- Dashboard page load: Test API call, Realtime subscription, card rendering
- BPO review workflow: Test navigation to pending reviews, detail view, approve/edit/discard actions, toast notifications

**End-to-End (E2E) Tests:**
- **E2E-4.1:** Login as Admin, verify admin dashboard cards displayed
- **E2E-4.2:** Login as BPO, navigate to pending reviews, approve a suggestion, verify active record created and audit log entry exists
- **E2E-4.3:** Login as BPO, edit a suggestion, approve, verify active record has edited values and change log visible
- **E2E-4.4:** Login as BPO, discard a suggestion, verify status updated to "archived"
- **E2E-4.5:** Simulate Realtime update (update control status in database), verify dashboard refreshes within 1 minute
- **E2E-4.6:** Login as non-BPO user, attempt to access `/dashboard/bpo/reviews`, verify 403 error

**Performance Tests:**
- Dashboard load time: Lighthouse audit, verify LCP < 2.5s
- Dashboard metrics API: Load test with 50 concurrent requests, verify p95 < 500ms
- Realtime subscription: Simulate 50 concurrent users, trigger database update, measure time to all clients receiving update

**Security Tests:**
- Attempt cross-tenant access (BPO from Tenant A tries to access Tenant B's suggestions), verify 403/404
- Attempt to bypass residual_risk validation by sending malformed request, verify 400 error
- Verify JWT required for all endpoints, verify 401 when missing/invalid

**Acceptance Testing:**
- Execute all AC-4.1 through AC-4.9 test scenarios with manual verification
- Stakeholder demo: Show role-specific dashboards, real-time updates, and complete BPO assessment workflow

**Coverage Target:** 80% code coverage for backend services and frontend components
