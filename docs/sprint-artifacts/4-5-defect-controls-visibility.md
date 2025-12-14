# Story 4.5: Defect - Approved Controls Visibility

**Status:** Ready for Dev
**Epic:** 4 - Real-Time Risk Monitoring & Assessment
**Priority:** High
**Estimation:** 1 Point

## User Story
**As a** Business Process Owner (BPO) or Admin,
**I want** to see approved controls (specifically those originating from suggestions like "Whistleblower") on the Controls page,
**So that** I can manage them effectively.

## Context & Scope
Currently, when a suggestion (e.g., "Whistleblower") is approved via the AI workflow, it is expected to become a visible, active control. However, it is not appearing on the `/controls` page for BPO or Admin users. This defect breaks the critical flow from "Suggestion" to "Active Control".

Investigation is needed to determine if the issue is in:
1.  **Persistence:** Is the control record actually created in the DB with the correct status?
2.  **API/Query:** Is the fetch query filtering it out (e.g., RLS issues, wrong status filter)?
3.  **Frontend:** Is the UI failing to render it?

## Acceptance Criteria
| ID | Criteria | Validation Method |
|----|----------|-------------------|
| AC-1 | **Database Integrity:** Approving a suggestion creates a `controls` record with status `active` (or equivalent). | Database Query |
| AC-2 | **API Visibility:** The `GET /api/v1/controls` endpoint includes the new control in its response for authorized users. | API Test (Curl/Postman) |
| AC-3 | **Dashboard Visibility:** The `/dashboard/controls` page displays the new control in the list. | UI Inspection |
| AC-4 | **Permissions:** BPO and Admin users can see these controls (RLS check). | Multi-role Login Test |

## Technical Implementation Tasks
- [ ] **Investigation**
    - [ ] Check `backend/app/api/v1/endpoints/suggestions.py` (or relevant controller) for the approval logic. Confirm `controls` table insertion.
    - [ ] Check `controls` table for the missing records.
    - [ ] Verify Row-Level Security (RLS) policies on `controls` table.
- [ ] **Fix Backend (if needed)**
    - [ ] Ensure `status` is set correctly upon creation.
    - [ ] Ensure `tenant_id` is correctly propagated.
- [ ] **Fix Frontend (if needed)**
    - [ ] Check `frontend/app/dashboard/controls/page.tsx` data fetching hook.
- [ ] **Verification**
    - [ ] Add regression test case for "Suggestion to Control" flow.

## Dev Notes
- **Context Reference:** [4.5.defect-controls-visibility.context.xml](../sprint-artifacts/4-5-defect-controls-visibility.context.xml)
- **Previous Learnings:** N/A (Previous story files not available).
- **Architecture:** Check `Supabase` RLS policies as a likely culprit for "visible to Admin but not BPO" or "not visible to anyone" if tenant ID is mismatched.