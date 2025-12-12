# Story 4.4: Dashboard UX Enhancements

Status: done

## Story

As a **user**,
I want **my user icon in the dashboard to display my name instead of a generic "U"**,
so that **the interface feels personalized and I can verify my identity at a glance**.

## Acceptance Criteria

1. **User Model Update**: The system stores a `full_name` (or `first_name`/`last_name`) for each user in the database.
2. **Avatar Display**: The dashboard header's user avatar displays the user's initials (e.g., "JD") derived from their name. If no name is set, it falls back to the email initial (current behavior).
3. **Tooltip/Menu**: Hovering or clicking the avatar displays the full name and role (e.g., "John Doe (Admin)").
4. **Persistence**: The name is loaded from the backend profile on login and persists across session refreshes.
5. **Profile Update (Optional)**: Users can optionally update their name via a simple profile settings interface (or just seeded for now if scope is tight). *Note: For this story, we will prioritize display. Updating might be a separate task or database seed.*

## Tasks / Subtasks

- [x] **Backend: Update User Schema** (AC: 1)
  - [x] Create Alembic migration to add `full_name` column to `public.users` table.
  - [x] Update SQLAlchemy `User` model in `backend/app/models/user.py`.
  - [x] Update Pydantic `UserRead` and `UserUpdate` schemas in `backend/app/schemas/__init__.py`.
- [x] **Backend: Update User Endpoints** (AC: 4)
  - [x] Ensure `GET /users/me` returns the new `full_name` field.
  - [x] (Optional) Update `PATCH /users/me` to allow updating `full_name`.
- [x] **Frontend: Update User Context** (AC: 4)
  - [x] Update frontend `User` type definition (`clientService` types).
  - [x] Ensure `useRole` or `useUser` hook fetches and stores the full profile.
- [x] **Frontend: Update UserNav Component** (AC: 2, 3)
  - [x] Locate `UserNav` or `Avatar` component (likely in `frontend/components/layout` or `dashboard`).
  - [x] Implement logic to derive initials from `full_name` (e.g., "John Doe" -> "JD").
  - [x] Update display to show Full Name in the dropdown/tooltip.
- [x] **Frontend: Integration**
  - [x] Verify the avatar updates correctly when the user logs in.

## Dev Notes

### Architecture & Patterns
- **Database Source of Truth**: The `public.users` table is the source of truth for application profile data, not Supabase `user_metadata` (though syncing is good practice, we rely on our DB).
- **Frontend State**: Ensure the user profile is cached/stored alongside the role to avoid waterfall requests.

### Source Tree Components
- `backend/app/models/user.py`
- `backend/alembic/versions/9f36641533ab_add_full_name_to_users.py` (New migration)
- `frontend/app/dashboard/layout.tsx`
- `frontend/lib/role.tsx`

### Learnings from Previous Story

**From Story 4.3 (Status: review)**

- **Frontend Structure**: Dashboard components are in `frontend/app/(dashboard)/...`. Shared components like the header are likely in `layout.tsx` or `components/dashboard`.
- **API Client**: We are using the generated `clientService`. After updating the backend schema, we must run `npm run generate-client` (or equivalent) to update frontend types.
- **Testing**: Frontend unit tests were missing in 4.3. Ensure `UserNav` has a test case for name rendering.

### References
- [Source: docs/epics.md#Story-4.4]

## Dev Agent Record

### Context Reference
- docs/sprint-artifacts/4-4-dashboard-ux-enhancements.context.xml

### Agent Model Used
Gemini 2.0 Flash

### Debug Log References

### Completion Notes List

**Completed Implementation:**
- Added `full_name` to Backend `User` model and Pydantic schemas.
- Created and applied Alembic migration `9f36641533ab_add_full_name_to_users.py`.
- Updated `frontend/lib/role.tsx` to fetch `full_name` from `/api/v1/users/me` and expose it in `useRole`.
- Updated `frontend/app/dashboard/layout.tsx` to display initials in Avatar and full name in Dropdown.
- Added Backend API test: `backend/tests/api/v1/test_user_fullname.py` (Passed).
- Added Frontend Component test: `frontend/__tests__/app/dashboard/layout.test.tsx` (Passed).

**Verification:**
- Verified Backend: API returns `full_name: null` by default and returns string when set.
- Verified Frontend: Layout correctly handles Name -> Initials (JD) and Null -> Fallback (U).

**Code Review Follow-up (2025-12-12):**
- ✅ Resolved review finding [Med]: Implemented email fallback in avatar initials (AC #2)
  - Updated `useRole` hook to fetch and return `email` from backend `/api/v1/users/me`
  - Modified `getInitials()` function to accept `email` parameter and fallback to email[0] when no name
  - Updated dashboard layout to pass email to getInitials
  - Added test case for email fallback scenario ("john@example.com" → "J")
  - All tests pass (4/4 frontend, 2/2 backend)

### File List
- `backend/app/models/user.py`
- `backend/app/schemas/__init__.py`
- `backend/alembic_migrations/versions/9f36641533ab_add_full_name_to_users.py`
- `backend/tests/api/v1/test_user_fullname.py`
- `frontend/lib/role.tsx`
- `frontend/app/dashboard/layout.tsx`
- `frontend/__tests__/app/dashboard/layout.test.tsx`

## Change Log

**2025-12-12** - Senior Developer Review notes appended. Status updated to in-progress (changes requested: AC #2 email fallback incomplete).

**2025-12-12** - Addressed code review findings - 1 item resolved. Implemented email fallback in avatar initials. All tests pass. Status updated to review.

**2025-12-12** - Senior Developer Review #2 completed. All ACs verified, all tests pass (6/6). Story approved and marked done.

---

## Senior Developer Review (AI)

**Reviewer:** BIP
**Date:** 2025-12-12
**Outcome:** Changes Requested

### Summary

Story 4.4 implements user name display in the dashboard avatar with strong test coverage and proper architectural patterns. The implementation successfully adds `full_name` to the user model, displays initials in the avatar, and shows the full name in the dropdown menu. However, one acceptance criterion (AC #2) is only partially implemented: the fallback behavior uses a generic "U" instead of deriving an initial from the user's email address as specified.

**Status Discrepancy Noted:** Story file shows Status: done, but sprint-status.yaml shows ready-for-dev. This inconsistency should be resolved.

### Key Findings

#### MEDIUM Severity

**[Med] AC #2 Fallback Behavior Incomplete (AC #2)**
- **Issue:** AC #2 states "If no name is set, it falls back to the email initial (current behavior)" but the implementation falls back to a hardcoded "U"
- **Evidence:** frontend/app/dashboard/layout.tsx:52 - `if (!name) return "U";`
- **Expected:** Derive initial from email address (e.g., "john@example.com" → "J")
- **Impact:** User experience is less personalized when full_name is not set; email-based fallback would provide better identification
- **Root Cause:** The `useRole` hook (frontend/lib/role.tsx) does not fetch or return email, even though it's available from the backend `/api/v1/users/me` endpoint (UserRead inherits from BaseUser which includes email)

### Acceptance Criteria Coverage

| AC # | Description | Status | Evidence |
|------|-------------|--------|----------|
| AC #1 | User Model Update: Store full_name in database | ✅ IMPLEMENTED | backend/app/models/user.py:15, backend/app/schemas/__init__.py:13, backend/alembic_migrations/versions/9f36641533ab_add_full_name_to_users.py:24 |
| AC #2 | Avatar Display: Show initials, fallback to email initial | ⚠️ PARTIAL | frontend/app/dashboard/layout.tsx:51-57 (initials logic ✓), line 52 (fallback to "U" instead of email ✗) |
| AC #3 | Tooltip/Menu: Display full name and role | ✅ IMPLEMENTED | frontend/app/dashboard/layout.tsx:229-232 |
| AC #4 | Persistence: Load from backend, persist across sessions | ✅ IMPLEMENTED | frontend/lib/role.tsx:41, useEffect handles auth state changes |
| AC #5 | Profile Update (Optional): Backend support for updating | ✅ IMPLEMENTED | backend/app/schemas/__init__.py:25 (UserUpdate includes full_name); frontend UI deferred per story note |

**Summary:** 4 of 5 acceptance criteria fully implemented, 1 partially implemented

### Task Completion Validation

| Task | Marked As | Verified As | Evidence |
|------|-----------|-------------|----------|
| Backend: Update User Schema | ✅ Complete | ✅ VERIFIED | Migration file exists, User model updated (user.py:15), schemas updated (__init__.py:13,19,25) |
| Backend: Update User Endpoints | ✅ Complete | ✅ VERIFIED | UserRead schema includes full_name; endpoint returns it; tests pass (test_user_fullname.py) |
| Frontend: Update User Context | ✅ Complete | ✅ VERIFIED | useRole hook fetches and returns fullName (role.tsx:41) |
| Frontend: Update UserNav Component | ✅ Complete | ✅ VERIFIED | getInitials function implemented (layout.tsx:51-57), dropdown shows fullName (layout.tsx:229) |
| Frontend: Integration | ✅ Complete | ✅ VERIFIED | Auth state change handler in useRole (role.tsx:65-98) ensures persistence |

**Summary:** 5 of 5 completed tasks verified, 0 questionable, 0 falsely marked complete

### Test Coverage and Gaps

**Backend Tests (backend/tests/api/v1/test_user_fullname.py):**
- ✅ Test: GET /users/me returns full_name: null by default
- ✅ Test: GET /users/me returns full_name when set
- **Status:** All tests pass (2/2) ✓

**Frontend Tests (frontend/__tests__/app/dashboard/layout.test.tsx):**
- ✅ Test: Displays initials from full name ("John Doe" → "JD")
- ✅ Test: Displays single initial for single name ("Admin" → "A")
- ✅ Test: Displays fallback "U" when no name
- **Status:** All tests pass (3/3) ✓

**Gap Identified:**
- Missing test case for email fallback behavior (would fail until AC #2 is fully implemented)

### Architectural Alignment

**✅ Architecture Compliance:**
- Follows established Next.js + FastAPI + Supabase architecture
- Proper separation: Database model → Pydantic schemas → API → Frontend hook → UI component
- Uses existing useRole hook pattern from Epic 2 (RBAC)
- Alembic migration follows standard practices (nullable column, proper revision chain)
- Tests organized in appropriate directories

**✅ Epic 4 Tech Spec Compliance:**
- Dashboard layout modifications align with Epic 4's role-specific dashboard objectives
- Uses Shadcn/UI Avatar component (consistent with Epic 4's UI component strategy)
- No conflicts with Epic 4's real-time updates or assessment workflows

**No architectural violations found.**

### Security Notes

**✅ No Security Issues Found:**
- `full_name` is a simple display field with no authentication/authorization implications
- Field is nullable, so no data integrity risks
- UserRead schema properly exposes the field (no sensitive data leakage)
- No input validation concerns (Pydantic handles type validation; String(100) limits length in DB)
- No injection risks (React automatically escapes JSX content)

### Best-Practices and References

**Tech Stack Detected:**
- **Backend:** FastAPI 0.115.0, SQLAlchemy, Alembic, Pydantic, pytest
- **Frontend:** Next.js (App Router), React, TypeScript, Shadcn/UI, Jest, React Testing Library

**Best-Practices Observed:**
- ✅ Database migration for schema changes (Alembic)
- ✅ Type safety with Pydantic (backend) and TypeScript (frontend)
- ✅ Test-driven approach (tests added for new functionality)
- ✅ Proper error handling in useRole (fallback to JWT if backend fails)
- ✅ Nullable column design (allows gradual adoption without breaking existing users)
- ✅ Component decomposition (getInitials helper function)

**References:**
- [FastAPI Users Documentation](https://fastapi-users.github.io/fastapi-users/) - BaseUser schema includes email field
- [Shadcn/UI Avatar Component](https://ui.shadcn.com/docs/components/avatar) - Used correctly with AvatarFallback
- [React Testing Library Best Practices](https://testing-library.com/docs/react-testing-library/intro/) - Tests follow recommended patterns

### Action Items

**Code Changes Required:**

- [x] [Med] Implement email fallback in avatar initials (AC #2) [file: frontend/lib/role.tsx:41, frontend/app/dashboard/layout.tsx:51-57]
  - Update `useRole` hook to fetch and return `email` from backend response
  - Modify `getInitials()` function signature to accept `email` as second parameter
  - Update fallback logic: if no name, derive initial from email (e.g., "john@example.com"[0].toUpperCase())
  - Update existing test case and add new test for email fallback scenario

**Advisory Notes:**

- Note: Resolve status discrepancy between story file (done) and sprint-status.yaml (ready-for-dev)
- Note: Consider adding a test case for the dropdown display showing full name (currently only avatar initials are tested)
- Note: Backend already supports PATCH /users/me for updating full_name; future story could add frontend profile settings UI

---

## Senior Developer Review #2 (AI) - Post-Fix Verification

**Reviewer:** BIP
**Date:** 2025-12-12
**Outcome:** Approve

### Summary

Story 4.4 has been successfully completed. The previously identified issue (AC #2 email fallback) has been fully resolved. All acceptance criteria are now implemented, all tests pass (6/6 total), and the code follows established patterns with no security concerns.

### Resolution Verification

**✅ AC #2 Email Fallback - RESOLVED**
- **Implementation Verified:**
  - `useRole` hook now fetches and returns `email` from `/api/v1/users/me` (frontend/lib/role.tsx:11, 43, 86, 111)
  - Email also extracted from JWT as fallback (lines 53, 92, 99)
  - `getInitials()` function updated to accept `email` parameter (frontend/app/dashboard/layout.tsx:51)
  - Proper fallback chain: name → email[0].toUpperCase() → "U" (lines 52-57, 60-65)
  - Avatar component correctly passes both fullName and email (line 235)
- **Test Coverage:**
  - New test added: "displays email initial when no name is set" ✅
  - All 4 frontend tests pass, including email fallback scenario
  - 2 backend tests pass (no regressions)

### Final Acceptance Criteria Status

| AC # | Description | Status | Evidence |
|------|-------------|--------|----------|
| AC #1 | User Model Update: Store full_name in database | ✅ IMPLEMENTED | backend/app/models/user.py:15, backend/app/schemas/__init__.py:13 |
| AC #2 | Avatar Display: Show initials, fallback to email initial | ✅ IMPLEMENTED | frontend/lib/role.tsx:11,43,111; frontend/app/dashboard/layout.tsx:51-57,235 |
| AC #3 | Tooltip/Menu: Display full name and role | ✅ IMPLEMENTED | frontend/app/dashboard/layout.tsx:241-244 |
| AC #4 | Persistence: Load from backend, persist across sessions | ✅ IMPLEMENTED | frontend/lib/role.tsx:41-43,67-106 |
| AC #5 | Profile Update (Optional): Backend support for updating | ✅ IMPLEMENTED | backend/app/schemas/__init__.py:25 |

**Summary:** 5 of 5 acceptance criteria fully implemented ✅

### Task Completion Validation

All 5 tasks remain verified as complete:
- ✅ Backend: Update User Schema
- ✅ Backend: Update User Endpoints
- ✅ Frontend: Update User Context (now includes email)
- ✅ Frontend: Update UserNav Component (now with email fallback)
- ✅ Frontend: Integration

**No false completions. All tasks genuinely implemented.**

### Test Results

**Backend Tests:** 2/2 pass ✅
**Frontend Tests:** 4/4 pass ✅ (added email fallback test)
**Total:** 6/6 tests pass

### Code Quality Assessment

**✅ Implementation Quality:**
- Clean, maintainable code with proper separation of concerns
- TypeScript types correctly updated
- Comprehensive error handling (backend fallback to JWT)
- Fallback chain properly implemented with defensive checks
- No code duplication

**✅ Best Practices:**
- Consistent with existing codebase patterns
- Proper React hooks usage (useState, useEffect)
- Good test coverage for all scenarios
- No magic strings or hardcoded values (except safe defaults)

**✅ Security:**
- No new security risks introduced
- Email is public user data, safe to display
- React automatic escaping prevents XSS
- No additional validation needed

### Approval Checklist

- [x] All acceptance criteria fully implemented and verified
- [x] All completed tasks genuinely done (no false completions)
- [x] All tests pass (100% pass rate)
- [x] No regressions introduced
- [x] Code quality meets standards
- [x] No security concerns
- [x] Previous review finding resolved with evidence

### Recommendation

**APPROVE for production.** Story is complete and ready to be marked `done`.

**No further action items required.**

