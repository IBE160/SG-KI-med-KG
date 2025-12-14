# Defect: Approved Controls Visibility

**Status:** Approved
**Point Value:** 1
**Priority:** High

## User Story
As a BPO or Admin, I want to see approved controls (specifically those originating from suggestions like "Whistleblower") on the Controls page so that I can manage them.

## Context
Currently, when a suggestion is approved (e.g., "Whistleblower"), it is supposed to become a visible Control. However, it is not appearing on the `/controls` page for BPO or Admin users. Investigation is needed to ensure the data is persisted correctly and the fetch query includes these records.

## Acceptance Criteria
- [ ] Verify that approving a suggestion creates a Control record in the database with the correct status (e.g., 'active').
- [ ] Verify that the API endpoint fetching controls (used by `/dashboard/controls`) includes these new records.
- [ ] Ensure any filtering (RLS or API level) allows BPO and Admin users to view these controls.
- [ ] The "Whistleblower" control is visible on the `/dashboard/controls` page.

## Technical Notes
- Frontend: `frontend/app/dashboard/controls/page.tsx`
- Backend Endpoint: Likely a `GET` on a controls resource. Check `backend/app/api` or `backend/app/routes`.
- Suspect issue in `backend/app/api/v1/endpoints/suggestions.py` (approval logic) or the fetching logic.
