# Story 4.4: Dashboard UX Enhancements

Status: drafted

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

- [ ] **Backend: Update User Schema** (AC: 1)
  - [ ] Create Alembic migration to add `full_name` column to `public.users` table.
  - [ ] Update SQLAlchemy `User` model in `backend/app/models/user.py`.
  - [ ] Update Pydantic `UserRead` and `UserUpdate` schemas in `backend/app/schemas/user.py`.
- [ ] **Backend: Update User Endpoints** (AC: 4)
  - [ ] Ensure `GET /users/me` returns the new `full_name` field.
  - [ ] (Optional) Update `PATCH /users/me` to allow updating `full_name`.
- [ ] **Frontend: Update User Context** (AC: 4)
  - [ ] Update frontend `User` type definition (`clientService` types).
  - [ ] Ensure `useRole` or `useUser` hook fetches and stores the full profile.
- [ ] **Frontend: Update UserNav Component** (AC: 2, 3)
  - [ ] Locate `UserNav` or `Avatar` component (likely in `frontend/components/layout` or `dashboard`).
  - [ ] Implement logic to derive initials from `full_name` (e.g., "John Doe" -> "JD").
  - [ ] Update display to show Full Name in the dropdown/tooltip.
- [ ] **Frontend: Integration**
  - [ ] Verify the avatar updates correctly when the user logs in.

## Dev Notes

### Architecture & Patterns
- **Database Source of Truth**: The `public.users` table is the source of truth for application profile data, not Supabase `user_metadata` (though syncing is good practice, we rely on our DB).
- **Frontend State**: Ensure the user profile is cached/stored alongside the role to avoid waterfall requests.

### Source Tree Components
- `backend/app/models/user.py`
- `backend/alembic/versions/` (New migration)
- `frontend/components/dashboard/user-nav.tsx` (Likely location, or similar)
- `frontend/lib/role.tsx` (If user state is managed here)

### Learnings from Previous Story

**From Story 4.3 (Status: review)**

- **Frontend Structure**: Dashboard components are in `frontend/app/(dashboard)/...`. Shared components like the header are likely in `layout.tsx` or `components/dashboard`.
- **API Client**: We are using the generated `clientService`. After updating the backend schema, we must run `npm run generate-client` (or equivalent) to update frontend types.
- **Testing**: Frontend unit tests were missing in 4.3. Ensure `UserNav` has a test case for name rendering.

### References
- [Source: docs/epics.md#Story-4.4]

## Dev Agent Record

### Context Reference
<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used
Gemini 2.0 Flash

### Debug Log References

### Completion Notes List

### File List
