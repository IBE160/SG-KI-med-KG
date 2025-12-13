# Story 3.6: Enhance Suggestions List UX

Status: ready-for-dev

## Story

As a **Compliance Officer (CO)**,
I want **the Suggestions list to display BPO assignment information and provide better filtering options**,
so that **I can quickly identify which suggestions are assigned, to whom, and filter suggestions by name/title in addition to type**.

## Acceptance Criteria

1. **Add "Assigned To" Column**
   - The Suggestions table includes a new "Assigned To" column between "Source Reference" and "Action".
   - For suggestions with `assigned_bpo_id` set, display the BPO's name (e.g., "Assigned to John Doe").
   - For suggestions without assignment, display "Unassigned" or "Not assigned" in muted text.
   - The column is sortable (alphabetically by BPO name or assignment status).
   - Clicking an assigned BPO name optionally shows a tooltip with role and email.

2. **Enhance Filter UI - Name/Title Search**
   - Add a search input field in the toolbar to filter suggestions by name/title.
   - The search filters suggestions in real-time as the user types (client-side).
   - The search is case-insensitive and matches partial strings.
   - Clear visual indicator when a name filter is active (e.g., "Searching for: [term]" badge).
   - Include a clear/reset button (X icon) in the search input to remove the filter.

3. **Improve Type Filter Integration**
   - Replace the separate "Filter by Type" dropdown (Story 3.5 implementation) with filter chips or tabs.
   - Filter chips: "All", "Risk", "Control", "Business Process" displayed as clickable badges/buttons.
   - Active filter is visually highlighted (e.g., primary color, bold).
   - Clicking an active chip deselects it and returns to "All".
   - Type and name filters work together (AND logic: show only items matching BOTH filters).

4. **Filter State Persistence**
   - Filter and sort state persists during the session (survives refetch after reviewing a suggestion).
   - State resets when navigating away from the page.
   - URL query parameters are NOT required (session-only state is acceptable).

## Tasks / Subtasks

- [ ] **Backend: Add BPO User Data to Suggestion Endpoint** (AC: 1)
  - [ ] Modify `GET /api/v1/suggestions` endpoint to include BPO user details (name, email) in response.
  - [ ] Use a JOIN or nested query to fetch `assigned_bpo` user information if `assigned_bpo_id` is set.
  - [ ] Update Pydantic schema to include optional `assigned_bpo` field with user info.

- [ ] **Frontend: Add "Assigned To" Column** (AC: 1)
  - [ ] Add new table column in `page.tsx` after "Source Reference".
  - [ ] Display BPO name if assigned, or "Unassigned" text if null.
  - [ ] Add sorting functionality for the "Assigned To" column.
  - [ ] Optional: Add tooltip showing BPO role and email on hover.

- [ ] **Frontend: Implement Name/Title Search Filter** (AC: 2)
  - [ ] Add search input field to the toolbar area (above the table).
  - [ ] Implement `useState` hook for search term.
  - [ ] Update `processedSuggestions` memo to filter by name/title using `getContentSummary`.
  - [ ] Add clear/reset button (X icon) inside the search input.
  - [ ] Display active search term as a badge when filtering.

- [ ] **Frontend: Replace Type Filter with Chips** (AC: 3)
  - [ ] Remove the Select dropdown (lines 186-196 in current `page.tsx`).
  - [ ] Create filter chip/button group: "All", "Risk", "Control", "Business Process".
  - [ ] Style active chip with primary color or bold styling.
  - [ ] Update `filterType` state on chip click.
  - [ ] Ensure type and name filters combine correctly in `processedSuggestions`.

- [ ] **Frontend: Persist Filter State During Session** (AC: 4)
  - [ ] Verify filter/sort state persists after `refetch()` (should work with existing `useState`).
  - [ ] Test that filters remain active after reviewing a suggestion.

- [ ] **Testing** (AC: 1, 2, 3, 4)
  - [ ] Integration test: Fetch suggestions with BPO assignment and verify `assigned_bpo` data is present.
  - [ ] Component test: Render "Assigned To" column with various assignment states.
  - [ ] Component test: Search filter correctly filters by name/title.
  - [ ] Component test: Type filter chips work and combine with name search.
  - [ ] Manual test: Verify filter state persists after reviewing a suggestion.

## Dev Notes

### Architecture Patterns

- **Backend Data Enrichment**: Use SQLAlchemy relationship loading or explicit JOIN to include BPO user data in the suggestion response. Avoid N+1 queries by using `joinedload` or similar.
- **Filter Chip Pattern**: Common UX pattern for faceted filtering. Use Shadcn/UI Button or Badge components styled as toggles.
- **Combined Filters**: The `processedSuggestions` memo should apply both type and name filters sequentially. Order: Filter by type → Filter by name → Sort.

### Source Tree Components

- `backend/app/api/v1/endpoints/suggestions.py` (Modified - Add BPO user JOIN)
- `backend/app/schemas/suggestion.py` (Modified - Add `assigned_bpo` field)
- `frontend/app/dashboard/admin/suggestions/page.tsx` (Modified - Add column, search, chips)
- `frontend/components/ui/input.tsx` (Used for search field - likely already exists)

### Testing Standards

- Mock the suggestions API response to include both assigned and unassigned items.
- Verify the search filter matches partial strings correctly (e.g., "risk" matches "Data Privacy Risk").
- Test edge case: Empty search string should show all items (no filter).
- Test edge case: Combining filters (e.g., "Risk" type + "GDPR" name search) shows correct subset.

### Project Structure Notes

**Alignment:**
- Standard backend/frontend structure maintained.
- Follows existing patterns from Story 3.5.

**Conflicts:** None detected.

### Learnings from Previous Story

**From Story 3-5-enhance-ai-review-capabilities (Status: done)**

- **New Components/Modifications:**
  - `frontend/app/dashboard/admin/suggestions/page.tsx` - Added sort (Type, Name, Date) and filter (Type dropdown) functionality. **Story 3.6 will replace the filter dropdown (lines 186-196) with chips.**
  - `backend/app/schemas/suggestion.py` - Extended schema with BPO assignment fields (`assigned_bpo_id`)
  - `backend/app/api/v1/endpoints/suggestions.py` - Added BPO validation on accept (requires `assigned_bpo_id`)
  - `frontend/components/custom/ai-review-mode/SuggestionList.tsx` - Integrated sort/filter UI
  - `backend/app/models/suggestion.py` - Extended `SuggestionType` enum with `business_process`
- **Filter Implementation**: Story 3.5 implemented basic type filtering with a Select dropdown (lines 186-196 in `page.tsx`). Story 3.6 will replace this with filter chips.
- **Sort/Filter Logic**: The `processedSuggestions` useMemo pattern works well. Extend it to handle name search without performance issues.
- **State Management**: Using local `useState` for filter/sort state is appropriate for this page. No need for global state.
- **BPO Assignment**: Story 3.5 made BPO assignment mandatory on acceptance. Story 3.6 displays this assignment in the "Assigned To" column.

[Source: docs/sprint-artifacts/3-5-enhance-ai-review-capabilities.md]

### References

- [Epic 3: AI-Powered Gap Analysis & Auditing](docs/epics.md#epic-3-ai-powered-gap-analysis--auditing) - Parent epic context
- [Epic Tech Spec: Epic 3](docs/sprint-artifacts/tech-spec-epic-3.md) - AI Review Mode context and Story 3.6 requirements
- [UX Design Specification](docs/ux-design-specification.md) - UI patterns for filters, search inputs, table enhancements, and visual indicators
- [Story 3.3: HITL Validation Interface](docs/sprint-artifacts/3-3-build-human-in-the-loop-hitl-validation-interface.md) - Original AI Review Mode implementation
- [Story 3.5: Enhance AI Review Capabilities](docs/sprint-artifacts/3-5-enhance-ai-review-capabilities.md) - Sorting and type filtering foundation

## Dev Agent Record

### Context Reference

- [Story Context](3-6-enhance-suggestions-list-ux.context.xml)

### Agent Model Used

<!-- Will be filled during development -->

### Debug Log References

<!-- Will be filled during development -->

### Completion Notes List

<!-- Will be filled during development -->

### File List

<!-- Will be filled during development -->

## Change Log

**2025-12-13** - Story drafted by Bob (Scrum Master). Post-MVP UX enhancement.
