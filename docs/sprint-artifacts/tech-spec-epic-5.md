# Epic Technical Specification: Advanced Compliance Mapping & Reporting

Date: 2025-12-12
Author: BIP
Epic ID: 5
Status: Draft

---

## Overview

Epic 5 delivers the **Advanced Compliance Mapping & Reporting** capability, fulfilling the critical FR-3 requirement for establishing and visualizing the relationship between internal controls and external regulatory requirements. This epic transforms the ibe160 platform from a risk and control management system into a comprehensive compliance framework that can demonstrate coverage, identify gaps, and support audit readiness.

Building on the foundational data model (Epic 1), authentication and RBAC (Epic 2), AI-powered suggestion generation (Epic 3), and real-time dashboards (Epic 4), this epic provides Admins and Executives with the tools to map controls to specific regulatory framework requirements and generate actionable gap analysis reports. This capability is essential for organizations navigating multiple regulatory frameworks (e.g., GDPR, SOX, ISO 27001) and needing to prove comprehensive compliance coverage.

## Objectives and Scope

**In Scope:**
- Design and implement a many-to-many junction table (`controls_regulatory_requirements`) to link controls to regulatory framework requirements
- Build an intuitive Admin-facing UI for managing compliance mappings (associating controls with requirements and vice versa)
- Implement multi-select or dual-list UI components for efficient mapping management
- Create a gap analysis report generation service that identifies unmapped regulatory requirements
- Build an Executive/Admin-facing report interface to view and export gap analysis results
- Support basic browser print-to-PDF export functionality for gap analysis reports
- Ensure all mapping operations respect tenant isolation and RBAC
- Optimize mapping and report queries for performance with large datasets

**Out of Scope:**
- Advanced report formatting or custom templates (basic structured output for MVP)
- Automated recommendations for control-to-requirement mappings (manual mapping only for MVP)
- Historical tracking of mapping changes over time (audit trail logs mapping actions, but no dedicated history view)
- Bulk import/export of mappings via CSV or Excel (manual UI-based mapping only)
- Custom report scheduling or automated delivery (on-demand generation only)
- Integration with third-party GRC platforms or regulatory databases

## System Architecture Alignment

This epic aligns with the decoupled Next.js (frontend) + FastAPI (backend) + Supabase architecture:

- **Frontend (Next.js):** Compliance mapping UI will live in `frontend/app/(dashboard)/admin/compliance-mapping` with dual-list or multi-select components from Shadcn/UI. Gap analysis report interface will be in `frontend/app/(dashboard)/reports/gap-analysis` accessible to Admins and Executives. The UI leverages the "Clarity Green" (light) and "Focused Slate" (dark) themes defined in the UX specification.

- **Backend (FastAPI):** New API endpoints in `backend/app/api/v1/mapping.py` and `backend/app/api/v1/reports.py` will handle mapping CRUD operations and gap analysis report generation. The mapping service will leverage SQLAlchemy ORM to manage the many-to-many relationship via the junction table.

- **Database (Supabase PostgreSQL):** A new `controls_regulatory_requirements` junction table will be created with foreign keys to `controls` and `regulatory_frameworks` tables. Row-Level Security (RLS) policies will enforce tenant isolation on the junction table.

- **State Management:** React Query manages server state for mapping operations and report data. Optimistic updates for mapping additions/removals provide instant UI feedback.

- **Performance:** Database indexes on `control_id`, `regulatory_requirement_id`, and `tenant_id` ensure efficient mapping queries and gap analysis aggregation. Query results cached with React Query for 60-second TTL.

## Detailed Design

### Services and Modules

| Module/Service | Location | Responsibilities | Inputs | Outputs | Owner |
|---|---|---|---|---|---|
| **MappingService** | `backend/app/services/mapping_service.py` | Manages CRUD operations for control-to-requirement mappings; enforces tenant isolation and authorization | `control_id`, `regulatory_requirement_id`, `tenant_id`, `user_id` | Mapping record created/deleted, list of mappings for a control or requirement | Backend Dev |
| **GapAnalysisService** | `backend/app/services/gap_analysis_service.py` | Queries database to identify regulatory requirements with no associated controls; generates structured gap report | `regulatory_framework_id`, `tenant_id` | Gap analysis report (JSON with unmapped requirements, coverage metrics) | Backend Dev |
| **MappingCRUD** | `backend/app/crud/mapping.py` | Database interaction layer for junction table operations; uses SQLAlchemy ORM | SQLAlchemy models, filter criteria | Database query results (mappings) | Backend Dev |
| **ComplianceMappingUI** | `frontend/app/(dashboard)/admin/compliance-mapping/page.tsx` | Admin interface for managing control-requirement mappings with dual-list or multi-select components | Selected control or regulatory framework | Interactive mapping management UI | Frontend Dev |
| **GapAnalysisReportUI** | `frontend/app/(dashboard)/reports/gap-analysis/page.tsx` | Admin/Executive interface for viewing and printing gap analysis reports | Selected regulatory framework | Formatted report display with print capability | Frontend Dev |
| **DualListSelector** | `frontend/components/custom/DualListSelector.tsx` | Reusable component for many-to-many mapping (shows available items on left, selected items on right with move actions) | `availableItems`, `selectedItems`, `onAdd`, `onRemove` | User interaction events (item added/removed) | Frontend Dev |

### Data Models and Contracts

**Database Schema: Junction Table**

```sql
-- backend/migrations/versions/XXX_create_controls_regulatory_requirements.py
CREATE TABLE controls_regulatory_requirements (
    id SERIAL PRIMARY KEY,
    control_id INTEGER NOT NULL REFERENCES controls(id) ON DELETE CASCADE,
    regulatory_requirement_id INTEGER NOT NULL REFERENCES regulatory_frameworks(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(control_id, regulatory_requirement_id, tenant_id)
);

CREATE INDEX idx_crr_control_id ON controls_regulatory_requirements(control_id);
CREATE INDEX idx_crr_requirement_id ON controls_regulatory_requirements(regulatory_requirement_id);
CREATE INDEX idx_crr_tenant_id ON controls_regulatory_requirements(tenant_id);

-- Row-Level Security Policy
ALTER TABLE controls_regulatory_requirements ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON controls_regulatory_requirements
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

**SQLAlchemy Model**

```python
# backend/app/models/mapping.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class ControlRegulatoryRequirement(Base):
    __tablename__ = "controls_regulatory_requirements"

    id = Column(Integer, primary_key=True, index=True)
    control_id = Column(Integer, ForeignKey("controls.id", ondelete="CASCADE"), nullable=False)
    regulatory_requirement_id = Column(Integer, ForeignKey("regulatory_frameworks.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    control = relationship("Control", back_populates="regulatory_mappings")
    regulatory_requirement = relationship("RegulatoryFramework", back_populates="control_mappings")

    __table_args__ = (
        UniqueConstraint('control_id', 'regulatory_requirement_id', 'tenant_id', name='unique_control_requirement_per_tenant'),
    )
```

**API Request/Response Schemas**

```python
# backend/app/schemas/mapping.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MappingCreate(BaseModel):
    """Request to create a new control-requirement mapping"""
    control_id: int
    regulatory_requirement_id: int

class MappingDelete(BaseModel):
    """Request to delete a mapping"""
    control_id: int
    regulatory_requirement_id: int

class MappingDetail(BaseModel):
    """Single mapping record"""
    id: int
    control_id: int
    regulatory_requirement_id: int
    control_name: str
    requirement_name: str
    created_at: datetime
    created_by: int

class MappingListResponse(BaseModel):
    """List of mappings for a control or requirement"""
    total: int
    mappings: List[MappingDetail]

# backend/app/schemas/reports.py
from pydantic import BaseModel
from typing import List

class UnmappedRequirement(BaseModel):
    """A regulatory requirement with no associated controls"""
    requirement_id: int
    requirement_name: str
    requirement_description: Optional[str] = None
    framework_name: str

class GapAnalysisReport(BaseModel):
    """Complete gap analysis report for a regulatory framework"""
    framework_id: int
    framework_name: str
    total_requirements: int
    mapped_requirements: int
    unmapped_requirements: int
    coverage_percentage: float
    gaps: List[UnmappedRequirement]
```

### APIs and Interfaces

**Create Mapping**

- **Method:** `POST`
- **Path:** `/api/v1/mappings`
- **Auth:** Required (Admin role)
- **Request Body:** `MappingCreate`
- **Response:** `MappingDetail` (201 Created)
- **Error:**
  - `400 Bad Request` (invalid control_id or regulatory_requirement_id)
  - `409 Conflict` (mapping already exists)
  - `403 Forbidden` (non-Admin user)
- **Side Effects:** Creates junction table record; logs action to audit trail

**Delete Mapping**

- **Method:** `DELETE`
- **Path:** `/api/v1/mappings`
- **Auth:** Required (Admin role)
- **Request Body:** `MappingDelete`
- **Response:** `204 No Content`
- **Error:**
  - `404 Not Found` (mapping doesn't exist)
  - `403 Forbidden` (non-Admin user)
- **Side Effects:** Deletes junction table record; logs action to audit trail

**Get Mappings for Control**

- **Method:** `GET`
- **Path:** `/api/v1/mappings/control/{control_id}`
- **Auth:** Required (Admin, Executive, or BPO role)
- **Response:** `MappingListResponse` (200 OK)
- **Error:** `404 Not Found` (control doesn't exist or not in user's tenant)

**Get Mappings for Requirement**

- **Method:** `GET`
- **Path:** `/api/v1/mappings/requirement/{requirement_id}`
- **Auth:** Required (Admin, Executive, or BPO role)
- **Response:** `MappingListResponse` (200 OK)
- **Error:** `404 Not Found` (requirement doesn't exist or not in user's tenant)

**Generate Gap Analysis Report**

- **Method:** `GET`
- **Path:** `/api/v1/reports/gap-analysis/{framework_id}`
- **Auth:** Required (Admin or Executive role)
- **Response:** `GapAnalysisReport` (200 OK)
- **Error:**
  - `404 Not Found` (framework doesn't exist or not in user's tenant)
  - `403 Forbidden` (non-Admin/Executive user)
- **Description:** Queries all requirements in the framework and identifies those with zero associated controls

### Workflows and Sequencing

**Workflow 1: Admin Creates Control-to-Requirement Mapping**

1. Admin navigates to `/dashboard/admin/compliance-mapping`
2. Admin selects a control from the control list
3. Frontend calls `GET /api/v1/mappings/control/{control_id}` to fetch existing mappings
4. Backend MappingCRUD queries `controls_regulatory_requirements` table filtered by `control_id` and `tenant_id`
5. Backend returns list of currently mapped requirements
6. Frontend displays dual-list selector: left side shows available (unmapped) requirements, right side shows mapped requirements
7. Admin selects one or more requirements from the left and clicks "Add Mapping"
8. Frontend sends `POST /api/v1/mappings` for each new mapping (or batched if API supports)
9. Backend MappingService validates control and requirement exist in the same tenant
10. Backend creates record in `controls_regulatory_requirements` table with `created_by` = current user
11. Backend logs mapping action to audit trail
12. Backend returns `201 Created` with mapping details
13. Frontend optimistically updates UI (moves requirement from left to right list)
14. Frontend displays success toast: "✅ Mapping created"

**Workflow 2: Admin Removes Mapping**

1. Admin is in compliance mapping UI with a control selected
2. Admin clicks "Remove" button next to a mapped requirement on the right side of dual-list
3. Frontend sends `DELETE /api/v1/mappings` with `control_id` and `regulatory_requirement_id`
4. Backend MappingService validates mapping exists and user is Admin
5. Backend deletes record from junction table
6. Backend logs deletion to audit trail
7. Backend returns `204 No Content`
8. Frontend optimistically updates UI (moves requirement from right to left list)
9. Frontend displays success toast: "✅ Mapping removed"

**Workflow 3: Executive Generates Gap Analysis Report**

1. Executive navigates to `/dashboard/reports/gap-analysis`
2. Frontend displays list of available regulatory frameworks (fetched from `GET /api/v1/regulatory-frameworks`)
3. Executive selects a framework (e.g., "GDPR") and clicks "Generate Report"
4. Frontend calls `GET /api/v1/reports/gap-analysis/{framework_id}`
5. Backend GapAnalysisService executes the following query logic:
   - Count total requirements in the framework: `SELECT COUNT(*) FROM regulatory_frameworks WHERE id = {framework_id}`
   - Identify unmapped requirements:
     ```sql
     SELECT rf.id, rf.name, rf.description
     FROM regulatory_frameworks rf
     LEFT JOIN controls_regulatory_requirements crr ON rf.id = crr.regulatory_requirement_id
     WHERE rf.id = {framework_id} AND crr.id IS NULL AND rf.tenant_id = {tenant_id}
     ```
   - Count mapped requirements: `total_requirements - unmapped_count`
   - Calculate coverage percentage: `(mapped / total) * 100`
6. Backend returns `GapAnalysisReport` JSON
7. Frontend renders structured report with sections:
   - Framework name and overview
   - Coverage metrics (e.g., "75% coverage: 45 of 60 requirements mapped")
   - Table of unmapped requirements (requirement name, description)
8. Executive clicks "Print Report" button
9. Browser print dialog opens with print-optimized CSS (hide nav, buttons, etc.)
10. Executive prints to PDF or physical printer

**Workflow 4: Admin Manages Mapping from Requirement Perspective**

1. Admin navigates to `/dashboard/admin/compliance-mapping?view=requirement`
2. Admin selects a regulatory requirement from the requirement list
3. Frontend calls `GET /api/v1/mappings/requirement/{requirement_id}`
4. Backend returns list of controls currently mapped to this requirement
5. Frontend displays dual-list selector: left shows available (unmapped) controls, right shows mapped controls
6. Admin can add/remove control mappings using the same `POST`/`DELETE` endpoints as Workflow 1 & 2
7. Mapping creation/deletion follows identical backend logic with roles reversed (control vs. requirement perspective)

## Non-Functional Requirements

### Performance

- **Mapping Creation Response Time:** `POST /api/v1/mappings` must complete within 300ms under normal load (simple INSERT operation with validation)
- **Mapping Query Response Time:** `GET /api/v1/mappings/control/{id}` and `GET /api/v1/mappings/requirement/{id}` must respond within 400ms even for controls/requirements with 100+ mappings
- **Gap Analysis Report Generation:** `GET /api/v1/reports/gap-analysis/{framework_id}` must complete within 2 seconds for frameworks with up to 500 requirements
- **Database Index Performance:** Junction table queries must leverage indexes on `control_id`, `requirement_id`, and `tenant_id` to achieve sub-100ms query times
- **UI Responsiveness:** Dual-list selector component must support instant drag-and-drop or click-to-move actions with optimistic UI updates
- **Report Rendering:** Gap analysis report page must render with LCP < 2.5 seconds (consistent with dashboard performance target)
- **Concurrent Mapping Operations:** System must support at least 10 concurrent Admins creating/deleting mappings per tenant without performance degradation
- **React Query Caching:** Mapping lists and gap reports cached with 60-second TTL to reduce API load; cache invalidated immediately on create/delete actions

**Performance Optimizations:**
- Database query uses LEFT JOIN for gap analysis to identify unmapped requirements in a single query
- Pagination support for large mapping lists (page size: 50 items)
- Frontend uses virtualized lists (e.g., react-window) if mapping lists exceed 200 items
- Print-optimized CSS loaded only when print action triggered

### Security

- **Authentication:** All mapping and report endpoints require valid JWT token in `Authorization: Bearer <token>` header; return 401 if missing/invalid
- **Role-Based Authorization:**
  - Mapping create/delete endpoints (`POST`/`DELETE /api/v1/mappings`) enforce Admin role check; return 403 if non-Admin attempts access
  - Gap analysis report endpoint (`GET /api/v1/reports/gap-analysis/{id}`) enforces Admin or Executive role; return 403 for BPO or General User
  - Mapping query endpoints (`GET /api/v1/mappings/*`) accessible to Admin, Executive, and BPO roles for read-only visibility
- **Tenant Isolation:**
  - All database queries filter by `tenant_id` via Row-Level Security (RLS) policies
  - Backend validates that `control_id` and `regulatory_requirement_id` in mapping requests belong to the authenticated user's tenant; return 404 if cross-tenant access attempted
  - Junction table enforces tenant isolation via RLS policy on `controls_regulatory_requirements` table
- **Input Validation:**
  - All API request payloads validated via Pydantic schemas; reject malformed requests with 400 Bad Request
  - Control_id and requirement_id must reference existing records in the tenant; return 400 if invalid IDs provided
  - Unique constraint on junction table prevents duplicate mappings; return 409 Conflict if duplicate attempted
- **Audit Logging:** All mapping create/delete actions logged to immutable audit trail with user identity, timestamp, and action details (control_id, requirement_id)
- **XSS Prevention:** All user-generated content (control names, requirement descriptions) sanitized before rendering in frontend reports
- **SQL Injection Protection:** All database queries use parameterized statements via SQLAlchemy ORM; no raw SQL with string interpolation

### Reliability/Availability

- **Service Uptime:** Mapping and report endpoints must maintain 99.5% uptime (consistent with Vercel/Railway SLA targets)
- **Graceful Degradation:**
  - If gap analysis report generation fails (database timeout, query error), frontend displays cached report (if available) with warning banner: "Report may be outdated, generated at [timestamp]"
  - If mapping creation fails (network error, backend error), frontend displays clear error toast and does NOT optimistically update UI (rolls back optimistic change)
- **Error Handling:**
  - If gap analysis query times out (>5 seconds), backend returns 504 Gateway Timeout with message: "Report generation exceeded time limit, try a smaller framework or contact support"
  - If mapping deletion fails due to foreign key constraint violation (shouldn't happen with CASCADE), return 500 Internal Server Error with logged exception
- **Data Consistency:**
  - Mapping create/delete actions are atomic; if audit logging fails, entire transaction rolls back (no orphaned mapping records)
  - Duplicate mapping prevention via unique constraint ensures data integrity
- **Idempotency:**
  - Mapping creation is idempotent; duplicate `POST /api/v1/mappings` requests return 409 Conflict without creating duplicate records
  - Mapping deletion is idempotent; deleting a non-existent mapping returns 404 (not 500)
- **Database CASCADE Behavior:**
  - If a control or regulatory requirement is deleted, associated mappings are automatically deleted via `ON DELETE CASCADE` foreign key constraint
  - No orphaned mapping records left in junction table

### Observability

- **Backend Logging:**
  - All mapping create/delete operations logged with `user_id`, `tenant_id`, `control_id`, `requirement_id`, `action` (create/delete), duration
  - All gap analysis report generation logged with `user_id`, `tenant_id`, `framework_id`, `unmapped_count`, query duration
  - Errors logged with full stack trace, request context, and user information
  - Slow queries (>1 second) logged with query plan for performance investigation
- **Frontend Monitoring:**
  - API call failures logged to frontend error tracking (e.g., Sentry integration if available)
  - Report rendering performance tracked (LCP, time-to-interactive)
  - Dual-list selector interaction events tracked (items added/removed, batch operations)
- **Metrics:**
  - Track count of mappings created/deleted per tenant per day
  - Track average number of mappings per control and per requirement
  - Track gap analysis report generation count per framework per tenant
  - Track coverage percentage distribution across all frameworks in the system
  - Track API endpoint response times (p50, p95, p99)
- **Alerts:**
  - Alert if mapping creation endpoint p95 latency exceeds 500ms
  - Alert if gap analysis report generation endpoint error rate exceeds 5%
  - Alert if gap analysis query duration exceeds 3 seconds (p95)
  - Alert if junction table row count exceeds 100,000 (may indicate performance degradation risk)
- **Database Query Monitoring:**
  - Monitor index usage on junction table; alert if full table scans detected
  - Track query plan changes for gap analysis query after database updates

## Dependencies and Integrations

**External Dependencies (from package.json & pyproject.toml):**

| Dependency | Version | Purpose | Integration Point |
|---|---|---|---|
| **Backend Dependencies** |  |  |  |
| `fastapi[standard]` | v0.115.0+ | Web framework for API endpoints | Backend: All endpoints in `backend/app/api/v1/mapping.py` and `backend/app/api/v1/reports.py` |
| `pydantic` | v2.5.2+ (via fastapi) | Request/response validation, schemas | Backend: `backend/app/schemas/mapping.py`, `backend/app/schemas/reports.py` |
| `sqlalchemy` | (via fastapi-users) | ORM for database queries | Backend: `backend/app/models/mapping.py`, `backend/app/crud/mapping.py` |
| `asyncpg` | v0.29.0+ | PostgreSQL async driver | Backend: All database operations via SQLAlchemy |
| `alembic` | v1.14.0+ | Database migrations | Backend: Migration script for `controls_regulatory_requirements` table in `backend/migrations/` |
| **Frontend Dependencies** |  |  |  |
| `@supabase/supabase-js` | v2.86.2 | Supabase client for auth and database | Frontend: `frontend/lib/supabase.ts`, used for JWT token management |
| `@tanstack/react-query` | v5.90.12 | Server state management, caching, mutations | Frontend: Wraps all API calls, manages mapping and report data cache |
| `react-hook-form` | v7.54.0 | Form state management | Frontend: Used in dual-list selector for managing selections |
| `zod` | v3.23.8 | Client-side validation | Frontend: Validates mapping create/delete requests before API calls |
| `@radix-ui/react-dialog` | v1.1.15 | Modal/dialog primitives (Shadcn/UI) | Frontend: Confirmation dialogs for mapping deletion |
| `@radix-ui/react-select` | v2.2.5 | Select dropdown primitives (Shadcn/UI) | Frontend: Framework selector in gap analysis report UI |
| `sonner` | v2.0.7 | Toast notifications | Frontend: Success/error feedback for mapping operations |
| `lucide-react` | v0.452.0 | Icon library | Frontend: Icons for dual-list selector, report UI |
| `tailwindcss` | v4.1.17 | CSS framework | Frontend: Styling for all UI components |
| `next` | v15.5.0 | React framework | Frontend: App router pages in `frontend/app/(dashboard)/admin/compliance-mapping/` |

**Internal Module Dependencies:**

- **Epic 1 (Foundational Setup & Core Data Model):**
  - Mapping operations depend on `controls` and `regulatory_frameworks` tables created in Epic 1
  - MappingService queries these tables to validate control_id and requirement_id existence
  - Gap analysis report queries `regulatory_frameworks` table to get framework details
  - Junction table uses foreign keys to `controls.id` and `regulatory_frameworks.id`

- **Epic 2 (User Identity & Access Management):**
  - All mapping and report endpoints require authentication (JWT) from Epic 2
  - Admin role enforcement for mapping create/delete operations relies on RBAC from Epic 2
  - Executive role enforcement for gap analysis reports relies on RBAC from Epic 2
  - User identity extracted from JWT for `created_by` field in junction table

- **Epic 3 (AI-Powered Gap Analysis & Auditing):**
  - Mapping create/delete actions trigger audit log entries via Epic 3's `AuditLogService`
  - Audit logging ensures all compliance mapping changes are permanently recorded
  - MappingService calls `AuditLogService.log_action(action="create_mapping", user_id=..., details={...})`

- **Epic 4 (Real-Time Risk Monitoring & Assessment):**
  - Gap analysis reports may reference active controls/risks created via Epic 4's BPO assessment workflow
  - Dashboard integration: Gap analysis report link may appear on Executive dashboard (Epic 4)
  - Coverage metrics in gap analysis reports reflect the current state of active controls

**Integration Points:**

1. **Database Foreign Keys:**
   - `controls_regulatory_requirements.control_id` → `controls.id` (CASCADE delete)
   - `controls_regulatory_requirements.regulatory_requirement_id` → `regulatory_frameworks.id` (CASCADE delete)
   - When a control or requirement is deleted, all associated mappings are automatically removed

2. **Audit Logging Service (Epic 3):**
   - `MappingService.create_mapping()` calls `AuditLogService.log_action(action="create_mapping", user_id=..., control_id=..., requirement_id=..., timestamp=...)`
   - `MappingService.delete_mapping()` calls `AuditLogService.log_action(action="delete_mapping", ...)`
   - Integration ensures all mapping operations are auditable

3. **Authentication Middleware (Epic 2):**
   - All API endpoints decorated with `@requires_auth` middleware (validates JWT)
   - User role extracted from JWT claims for Admin/Executive authorization checks
   - Tenant_id extracted from JWT for tenant isolation queries

4. **Supabase Row-Level Security (RLS):**
   - Junction table inherits RLS policies from Epic 1 architecture
   - All queries automatically filtered by `tenant_id` via RLS policy
   - No cross-tenant data access possible

**Downstream Consumers:**

- **Future Compliance Features:**
  - Advanced compliance analytics may aggregate mapping data to show coverage trends over time
  - Custom reporting features may build on gap analysis report structure
  - Third-party GRC integrations may export/import mapping data

- **Executive Dashboards:**
  - Executive dashboard may display compliance coverage metrics derived from mapping data
  - "Compliance Health" card may show percentage of requirements mapped across all frameworks

- **Audit Reports:**
  - External auditors may request gap analysis reports as evidence of compliance coverage
  - Mapping change history (via audit trail) provides evidence of continuous compliance management

## Acceptance Criteria (Authoritative)

**AC-5.1: Junction Table Creation and Schema**
1. Database migration creates `controls_regulatory_requirements` table with all specified columns (id, control_id, regulatory_requirement_id, tenant_id, created_by, created_at)
2. Foreign key constraints established to `controls.id` and `regulatory_frameworks.id` with ON DELETE CASCADE
3. Unique constraint enforced on (control_id, regulatory_requirement_id, tenant_id) to prevent duplicate mappings
4. Indexes created on control_id, regulatory_requirement_id, and tenant_id columns
5. Row-Level Security (RLS) enabled on junction table with tenant isolation policy
6. SQLAlchemy model `ControlRegulatoryRequirement` correctly reflects table schema with relationships

**AC-5.2: Create Mapping Endpoint**
1. `POST /api/v1/mappings` endpoint accepts `MappingCreate` request body with control_id and regulatory_requirement_id
2. Endpoint requires valid JWT; returns 401 if missing/invalid
3. Endpoint requires Admin role; returns 403 if non-Admin user attempts access
4. Backend validates control_id and requirement_id exist in user's tenant; returns 400 if invalid IDs
5. Backend prevents duplicate mappings; returns 409 Conflict if mapping already exists
6. Successful creation returns 201 Created with `MappingDetail` response including control_name and requirement_name
7. Mapping record includes tenant_id and created_by from authenticated user
8. Audit log entry created with action="create_mapping", user_id, control_id, requirement_id, timestamp

**AC-5.3: Delete Mapping Endpoint**
1. `DELETE /api/v1/mappings` endpoint accepts `MappingDelete` request body with control_id and regulatory_requirement_id
2. Endpoint requires valid JWT; returns 401 if missing/invalid
3. Endpoint requires Admin role; returns 403 if non-Admin user attempts access
4. Backend deletes mapping record if exists; returns 204 No Content
5. Backend returns 404 Not Found if mapping doesn't exist
6. Audit log entry created with action="delete_mapping", user_id, control_id, requirement_id, timestamp
7. Deletion is idempotent; repeated delete requests for same mapping return 404 (not 500)

**AC-5.4: Get Mappings for Control Endpoint**
1. `GET /api/v1/mappings/control/{control_id}` endpoint returns `MappingListResponse` with list of all requirements mapped to the control
2. Endpoint requires valid JWT; returns 401 if missing/invalid
3. Endpoint accessible to Admin, Executive, and BPO roles (read-only visibility)
4. Backend filters mappings by user's tenant_id; no cross-tenant data returned
5. Response includes control_name, requirement_name for each mapping
6. Returns 404 if control doesn't exist or not in user's tenant
7. Returns 200 OK with empty list if control has zero mappings

**AC-5.5: Get Mappings for Requirement Endpoint**
1. `GET /api/v1/mappings/requirement/{requirement_id}` endpoint returns `MappingListResponse` with list of all controls mapped to the requirement
2. Endpoint requires valid JWT; returns 401 if missing/invalid
3. Endpoint accessible to Admin, Executive, and BPO roles (read-only visibility)
4. Backend filters mappings by user's tenant_id; no cross-tenant data returned
5. Response includes control_name, requirement_name for each mapping
6. Returns 404 if requirement doesn't exist or not in user's tenant
7. Returns 200 OK with empty list if requirement has zero mappings

**AC-5.6: Compliance Mapping UI (Admin)**
1. Admin can navigate to `/dashboard/admin/compliance-mapping` page
2. Page displays list of all controls in the tenant (fetched from Epic 1 endpoints)
3. Admin can select a control from the list
4. Upon selection, frontend calls `GET /api/v1/mappings/control/{id}` to fetch existing mappings
5. Dual-list selector component renders with left panel showing available (unmapped) requirements and right panel showing mapped requirements
6. Admin can select one or more requirements from left panel and click "Add Mapping" button
7. Frontend sends `POST /api/v1/mappings` for each new mapping
8. UI optimistically updates (moves requirement from left to right) while API call is in progress
9. Success toast displayed: "✅ Mapping created"
10. If API call fails, optimistic update is rolled back and error toast displayed

**AC-5.7: Compliance Mapping UI - Remove Mapping**
1. Admin can click "Remove" button next to a mapped requirement in right panel of dual-list selector
2. Frontend sends `DELETE /api/v1/mappings` with control_id and requirement_id
3. UI optimistically updates (moves requirement from right to left) while API call is in progress
4. Success toast displayed: "✅ Mapping removed"
5. If API call fails, optimistic update is rolled back and error toast displayed

**AC-5.8: Compliance Mapping UI - Requirement Perspective**
1. Admin can toggle view to "Requirement Perspective" (e.g., via tab or URL parameter `?view=requirement`)
2. Page displays list of all regulatory requirements in the tenant
3. Admin can select a requirement from the list
4. Upon selection, frontend calls `GET /api/v1/mappings/requirement/{id}` to fetch existing mappings
5. Dual-list selector displays available (unmapped) controls on left and mapped controls on right
6. Add/remove mapping operations function identically to control perspective using same API endpoints

**AC-5.9: Gap Analysis Report Generation Endpoint**
1. `GET /api/v1/reports/gap-analysis/{framework_id}` endpoint generates gap analysis report
2. Endpoint requires valid JWT; returns 401 if missing/invalid
3. Endpoint requires Admin or Executive role; returns 403 for BPO or General User
4. Backend validates framework_id exists in user's tenant; returns 404 if invalid
5. Backend executes LEFT JOIN query to identify requirements with zero associated controls
6. Backend calculates total_requirements, mapped_requirements, unmapped_requirements, coverage_percentage
7. Response returns `GapAnalysisReport` with framework details and list of unmapped requirements (200 OK)
8. Report generation completes within 2 seconds for frameworks with up to 500 requirements
9. If query times out (>5 seconds), returns 504 Gateway Timeout with error message

**AC-5.10: Gap Analysis Report UI**
1. Admin/Executive can navigate to `/dashboard/reports/gap-analysis` page
2. Page displays dropdown to select a regulatory framework from list (fetched from `GET /api/v1/regulatory-frameworks`)
3. User selects framework and clicks "Generate Report" button
4. Frontend calls `GET /api/v1/reports/gap-analysis/{framework_id}`
5. Report renders with sections: framework name, coverage metrics (e.g., "75% coverage: 45 of 60 requirements mapped"), table of unmapped requirements
6. Each unmapped requirement displays requirement_name and requirement_description
7. Page renders with LCP < 2.5 seconds

**AC-5.11: Gap Analysis Report - Print to PDF**
1. Gap analysis report page includes "Print Report" button
2. Clicking button opens browser print dialog
3. Print-optimized CSS hides navigation, sidebar, and action buttons
4. Report content formatted for print/PDF export (A4 or Letter page size)
5. User can print to physical printer or save as PDF via browser print-to-PDF feature

**AC-5.12: Performance Requirements**
1. `POST /api/v1/mappings` responds within 300ms under normal load
2. `GET /api/v1/mappings/control/{id}` responds within 400ms for controls with 100+ mappings
3. `GET /api/v1/reports/gap-analysis/{id}` completes within 2 seconds for frameworks with 500 requirements
4. Database queries leverage indexes; junction table queries execute in <100ms
5. Dual-list selector supports instant drag-and-drop or click-to-move with optimistic UI updates

**AC-5.13: Security and Tenant Isolation**
1. All mapping and report endpoints enforce JWT authentication; return 401 if missing/invalid
2. Mapping create/delete operations enforce Admin role; return 403 for non-Admin users
3. Gap analysis reports enforce Admin or Executive role; return 403 for BPO or General User
4. All database queries filter by tenant_id via RLS policies; no cross-tenant access possible
5. Backend validates control_id and requirement_id belong to user's tenant; returns 404 if cross-tenant IDs provided
6. Audit trail logs all mapping create/delete operations with user identity and timestamp

**AC-5.14: Data Consistency and Reliability**
1. Unique constraint on junction table prevents duplicate mappings; duplicate POST returns 409 Conflict
2. Mapping create/delete operations are atomic; if audit logging fails, transaction rolls back
3. When a control or regulatory requirement is deleted, associated mappings are automatically deleted via CASCADE
4. No orphaned mapping records remain in junction table
5. Mapping deletion is idempotent; deleting non-existent mapping returns 404

## Traceability Mapping

| AC ID | Epic/Story | Spec Section | Component/API | Test Idea |
|---|---|---|---|---|
| AC-5.1 | Story 5.1 | Data Models: Database Schema, SQLAlchemy Model | Alembic migration script, `backend/app/models/mapping.py` | Test: Run migration, verify table created with correct schema, RLS enabled, indexes present |
| AC-5.2 | Story 5.1 | APIs: Create Mapping | `POST /api/v1/mappings`, MappingService | Test: Create mapping as Admin, verify 201 response, record in DB, audit log entry; test 403 as non-Admin |
| AC-5.3 | Story 5.1 | APIs: Delete Mapping | `DELETE /api/v1/mappings`, MappingService | Test: Delete existing mapping, verify 204 response, record removed from DB, audit log entry |
| AC-5.4 | Story 5.1 | APIs: Get Mappings for Control | `GET /api/v1/mappings/control/{id}`, MappingCRUD | Test: Create mappings, fetch for control, verify correct list returned; test tenant isolation |
| AC-5.5 | Story 5.1 | APIs: Get Mappings for Requirement | `GET /api/v1/mappings/requirement/{id}`, MappingCRUD | Test: Create mappings, fetch for requirement, verify correct list returned |
| AC-5.6 | Story 5.1 | Services: ComplianceMappingUI, DualListSelector | `frontend/app/(dashboard)/admin/compliance-mapping/page.tsx` | Test: Login as Admin, select control, add mapping via UI, verify optimistic update and API call |
| AC-5.7 | Story 5.1 | Workflows: Workflow 2 (Remove Mapping) | DualListSelector component, DELETE endpoint | Test: Remove mapping via UI, verify optimistic update, API call, success toast |
| AC-5.8 | Story 5.1 | Workflows: Workflow 4 (Requirement Perspective) | ComplianceMappingUI with view toggle | Test: Toggle to requirement view, select requirement, add control mapping, verify API call |
| AC-5.9 | Story 5.2 | APIs: Generate Gap Analysis Report, Services: GapAnalysisService | `GET /api/v1/reports/gap-analysis/{id}` | Test: Create mappings for framework, generate report, verify unmapped requirements identified correctly |
| AC-5.10 | Story 5.2 | Services: GapAnalysisReportUI | `frontend/app/(dashboard)/reports/gap-analysis/page.tsx` | Test: Login as Executive, select framework, generate report, verify coverage metrics and unmapped table displayed |
| AC-5.11 | Story 5.2 | Workflows: Workflow 3 (Print Report) | Print-optimized CSS, browser print dialog | Test: Click "Print Report", verify print dialog opens, print-optimized CSS hides nav/buttons |
| AC-5.12 | All Stories | NFR: Performance | All API endpoints, database indexes | Test: Load test mapping endpoints, verify response times; query plan analysis for gap analysis query |
| AC-5.13 | All Stories | NFR: Security | JWT middleware, role checks, RLS policies | Test: Attempt cross-tenant access, verify 403/404; attempt non-Admin mapping create, verify 403 |
| AC-5.14 | All Stories | NFR: Reliability, Data Models: Unique constraint, CASCADE | MappingService, database constraints | Test: Attempt duplicate mapping, verify 409; delete control, verify mappings CASCADE deleted |

## Risks, Assumptions, Open Questions

**RISK-5.1: Gap Analysis Query Performance at Scale**
- **Description:** The LEFT JOIN query for gap analysis may become slow as the number of regulatory requirements and controls grows (e.g., 1000+ requirements with 5000+ controls and 20,000+ mappings)
- **Impact:** Report generation exceeds 2-second target, degrading user experience and potentially timing out
- **Mitigation:**
  - Implement database query optimization with EXPLAIN ANALYZE during development
  - Add composite indexes on (regulatory_requirement_id, tenant_id) if needed
  - Consider materialized views for frequently-accessed gap analysis reports
  - Add pagination to gap analysis reports if full report becomes too large
  - Monitor query performance in production and optimize indexes based on actual usage patterns

**RISK-5.2: Dual-List Selector UX with Large Datasets**
- **Description:** If a tenant has hundreds of controls or requirements, the dual-list selector may become unwieldy with slow rendering and difficult navigation
- **Impact:** Admin users struggle to find and select items for mapping, reducing efficiency
- **Mitigation:**
  - Implement search/filter functionality in dual-list selector (filter by name)
  - Use virtualized lists (e.g., react-window) to render only visible items for lists >200 items
  - Add pagination or "load more" functionality for very large datasets
  - Consider alternative UI pattern (e.g., autocomplete multi-select) for extremely large tenants

**RISK-5.3: Mapping Data Model Limitations**
- **Description:** Current many-to-many model assumes simple control-to-requirement mappings without additional metadata (e.g., mapping strength, notes, effective date)
- **Impact:** Future requirements may necessitate schema changes and data migration
- **Mitigation:**
  - Document the simple mapping model as MVP scope; plan for schema extensions in post-MVP
  - Design junction table to allow adding columns without breaking existing queries
  - If additional metadata is requested during development, add optional columns (e.g., `notes TEXT`, `mapping_strength VARCHAR`) to avoid future migration

**RISK-5.4: Print-to-PDF Browser Compatibility**
- **Description:** Browser print-to-PDF functionality may produce inconsistent results across different browsers (Chrome, Firefox, Safari, Edge)
- **Impact:** Printed reports have formatting issues or missing content on certain browsers
- **Mitigation:**
  - Test print functionality on all major browsers during QA
  - Use CSS print media queries and test with @page rules for consistent pagination
  - Provide clear instructions to users on recommended browser for best print quality
  - Consider future enhancement: server-side PDF generation (e.g., using ReportLab or WeasyPrint in backend)

**ASSUMPTION-5.1: Regulatory Framework Structure**
- **Assumption:** The `regulatory_frameworks` table stores individual requirements (not just framework metadata), allowing direct mapping to controls
- **Validation Required:** Confirm with Epic 1 implementation that `regulatory_frameworks` table structure supports requirement-level granularity
- **Alternative:** If frameworks are stored separately from requirements, a new `regulatory_requirements` table may be needed with foreign key to `regulatory_frameworks`

**ASSUMPTION-5.2: Single Tenant Context**
- **Assumption:** A control or requirement belongs to exactly one tenant; cross-tenant sharing of controls/requirements is not required
- **Validation Required:** Confirm with stakeholders that tenants operate in complete isolation
- **Impact if False:** If cross-tenant sharing is needed, mapping model would require tenant context on both sides of the relationship

**ASSUMPTION-5.3: Mapping Approval Not Required**
- **Assumption:** Admin users can create/delete mappings without approval workflow; no review or validation step needed
- **Validation Required:** Confirm with compliance stakeholders that direct mapping is acceptable
- **Impact if False:** If approval is needed, would require extending the mapping model with status field (draft/approved) and approval workflow similar to Epic 3's HITL pattern

**ASSUMPTION-5.4: One-to-Many Control-Requirement Relationship**
- **Assumption:** Controls and requirements have a many-to-many relationship (one control can map to multiple requirements, one requirement can map to multiple controls)
- **Validation Required:** Confirm this is the correct business logic for compliance mapping
- **Impact if False:** If relationship is one-to-many or one-to-one, junction table design would be simplified

**QUESTION-5.1: Gap Analysis Report Scope**
- **Question:** Should gap analysis reports identify only unmapped requirements, or also controls that aren't mapped to any requirement ("orphaned controls")?
- **Impact:** If orphaned controls are in scope, requires additional query and report section
- **Decision Needed:** Clarify with stakeholders; for MVP, focus on unmapped requirements only (simpler and aligns with Story 5.2 AC)

**QUESTION-5.2: Mapping Change History**
- **Question:** Should there be a dedicated UI to view historical mapping changes (who mapped what, when), or is audit trail sufficient?
- **Impact:** Dedicated UI requires additional frontend development and query optimization for filtering audit logs
- **Decision Needed:** For MVP, rely on audit trail; defer dedicated mapping history UI to post-MVP enhancement

**QUESTION-5.3: Bulk Mapping Operations**
- **Question:** Should Admins be able to perform bulk mapping operations (e.g., map one control to 50 requirements at once, or import mappings from CSV)?
- **Impact:** Bulk operations require batch API endpoints, CSV parsing, and error handling for partial failures
- **Decision Needed:** For MVP, manual one-by-one mapping via dual-list selector; defer bulk operations to post-MVP

**QUESTION-5.4: Gap Analysis Scheduling**
- **Question:** Should gap analysis reports be generated on a schedule (e.g., weekly) and emailed to executives, or only on-demand via UI?
- **Impact:** Scheduled reports require background job setup (Celery), email template design, and user preference management
- **Decision Needed:** For MVP, on-demand generation only; defer scheduled reports to post-MVP

**QUESTION-5.5: Requirement Granularity**
- **Question:** Are regulatory requirements stored as individual, atomic items in the `regulatory_frameworks` table, or are they nested/hierarchical (e.g., sections with sub-requirements)?
- **Impact:** If hierarchical, gap analysis logic and UI must handle parent-child relationships
- **Decision Needed:** Clarify with Epic 1 implementation; assume flat structure for MVP

## Test Strategy Summary

**Unit Tests (Backend):**
- `MappingService.create_mapping()`: Test validation of control_id/requirement_id, duplicate prevention (409 Conflict), tenant isolation, audit logging
- `MappingService.delete_mapping()`: Test deletion, audit logging, 404 for non-existent mapping, idempotency
- `MappingCRUD.get_mappings_for_control()`: Test query filtering by control_id and tenant_id, empty list for zero mappings
- `MappingCRUD.get_mappings_for_requirement()`: Test query filtering by requirement_id and tenant_id
- `GapAnalysisService.generate_report()`: Test LEFT JOIN query logic, coverage percentage calculation, unmapped requirement identification
- Authorization middleware: Test Admin role enforcement for create/delete, Admin/Executive enforcement for gap analysis

**Unit Tests (Frontend):**
- `DualListSelector` component: Test item selection, add/remove actions, optimistic updates, error handling and rollback
- `ComplianceMappingUI` page: Test control/requirement selection, mapping list display, view toggle (control vs. requirement perspective)
- `GapAnalysisReportUI` page: Test framework selection, report rendering, coverage metrics display
- React Query hooks: Test cache invalidation on mapping create/delete, cache TTL behavior

**Integration Tests (Backend):**
- `POST /api/v1/mappings` (create): Test end-to-end flow from request to DB record to audit log; test 400 for invalid IDs, 409 for duplicates, 403 for non-Admin
- `DELETE /api/v1/mappings` (delete): Test end-to-end deletion flow; test 404 for non-existent mapping
- `GET /api/v1/mappings/control/{id}`: Test with real database, verify correct mappings returned, tenant isolation enforced
- `GET /api/v1/mappings/requirement/{id}`: Test with real database, verify correct mappings returned
- `GET /api/v1/reports/gap-analysis/{id}`: Test with real database containing mixed mapped/unmapped requirements; verify correct gap identification and metrics
- Database migration: Test Alembic migration creates junction table, indexes, RLS policies correctly; test rollback

**Integration Tests (Frontend):**
- Compliance mapping workflow: Test complete add mapping flow (select control, choose requirements, click add, verify API call and UI update)
- Remove mapping workflow: Test complete remove flow (click remove, verify API call and UI update)
- Gap analysis report workflow: Test select framework, generate report, verify data fetched and displayed
- Error handling: Test API failure scenarios (network error, 500 error), verify optimistic update rollback and error toast

**End-to-End (E2E) Tests:**
- **E2E-5.1:** Login as Admin, navigate to compliance mapping, select control, add mapping to requirement, verify mapping appears in right panel and success toast displayed
- **E2E-5.2:** Login as Admin, create mapping, remove mapping, verify it returns to left panel and success toast displayed
- **E2E-5.3:** Login as Admin, toggle to requirement view, select requirement, add control mapping, verify API call and UI update
- **E2E-5.4:** Login as Executive, navigate to gap analysis, select framework, generate report, verify coverage metrics and unmapped requirements table displayed
- **E2E-5.5:** Login as Executive, generate gap analysis report, click "Print Report", verify browser print dialog opens with print-optimized layout
- **E2E-5.6:** Login as BPO (non-Admin), attempt to navigate to `/dashboard/admin/compliance-mapping`, verify 403 error or redirect
- **E2E-5.7:** Login as General User (non-Executive), attempt to access gap analysis report, verify 403 error
- **E2E-5.8:** Create mapping as Admin, delete the control via Epic 1 UI, verify mapping is CASCADE deleted from junction table

**Performance Tests:**
- Mapping creation: Load test `POST /api/v1/mappings` with 100 concurrent requests, verify p95 latency < 300ms
- Mapping query: Test `GET /api/v1/mappings/control/{id}` with control having 100+ mappings, verify response time < 400ms
- Gap analysis: Test `GET /api/v1/reports/gap-analysis/{id}` with framework having 500 requirements, verify completion within 2 seconds
- Database query performance: Run EXPLAIN ANALYZE on gap analysis LEFT JOIN query, verify index usage, no full table scans
- UI rendering: Test dual-list selector with 500 items, verify virtualized rendering, no lag on scroll

**Security Tests:**
- Attempt to create mapping without JWT (missing Authorization header), verify 401 Unauthorized
- Attempt to create mapping as BPO (non-Admin), verify 403 Forbidden
- Attempt to access gap analysis report as BPO, verify 403 Forbidden
- Attempt cross-tenant mapping (Admin from Tenant A tries to map Control from Tenant B), verify 404 Not Found
- Verify audit trail logs all mapping create/delete operations with correct user_id and timestamp
- Test SQL injection prevention: Send malicious payloads in control_id/requirement_id, verify parameterized queries prevent injection

**Acceptance Testing:**
- Execute all AC-5.1 through AC-5.14 test scenarios with manual verification
- Stakeholder demo: Show Admin creating mappings via dual-list UI, Executive generating gap analysis report with print-to-PDF
- Compliance officer validation: Confirm gap analysis report output meets audit requirements

**Database Tests:**
- Unique constraint: Attempt to create duplicate mapping (same control_id, requirement_id, tenant_id), verify 409 Conflict error
- CASCADE deletion: Delete a control, verify all associated mappings deleted automatically
- RLS policy: Set `app.current_tenant_id` to Tenant A, query junction table, verify only Tenant A mappings returned
- Index usage: Query junction table by control_id, verify index scan (not sequential scan) in query plan

**Browser Compatibility Tests (Print Functionality):**
- Test gap analysis report print-to-PDF on Chrome, Firefox, Safari, Edge
- Verify print layout hides navigation/buttons, paginates correctly, includes all report content
- Test print preview and actual PDF output for formatting consistency

**Coverage Target:** 80% code coverage for backend services and frontend components
