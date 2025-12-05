# Story 3.3: Build Human-in-the-Loop (HITL) Validation Interface

Status: ready-for-dev

## Story

As a **Compliance Officer (CO)**,
I want **to use the two-stage "AI Review Mode" to efficiently triage AI suggestions and route them for final BPO approval**,
so that **I can act as an effective gatekeeper while ensuring business-level accountability**.

## Acceptance Criteria

1. **Two-pane view: List of suggestions vs Details.**
    - The interface presents a split view: a scrollable list of AI-generated suggestions on one side (e.g., left) and the detailed view of the selected suggestion on the other (e.g., right).
    - The list shows summary information (e.g., type, short description, confidence score if available).
    - The detail view shows full content, rationale, and source reference.
2. **CO can "Accept" (promote) or "Reject" (dismiss).**
    - For each suggestion, the CO has clear actions: "Accept" and "Reject" (or "Dismiss").
    - "Accept" promotes the suggestion to the next stage (BPO review).
    - "Reject" marks the suggestion as rejected and removes it from the active list.
    - The CO can optionally edit the content before accepting.
3. **Accepted items trigger notification (mocked or real) for BPO.**
    - When a suggestion is accepted, the system assigns it to a BPO (either manually selected by CO or auto-assigned based on metadata).
    - A notification event is triggered for the assigned BPO.
    - The suggestion status updates to "awaiting_bpo_approval".
4. **UI updates immediately upon action.**
    - The list view updates instantly after an action is taken (optimistic UI or fast re-fetch).
    - The next item in the list is automatically selected.

## Tasks / Subtasks

- [ ] **Backend: Implement Suggestion Review Endpoints** (AC: 2, 3)
  - [ ] Create `PATCH /api/v1/suggestions/{id}/status` endpoint.
  - [ ] Handle status transitions: `pending` -> `awaiting_bpo_approval` (Accept) or `rejected` (Reject).
  - [ ] Allow updating content (`risk_description`, `control_description`) during transition.
  - [ ] Implement BPO assignment logic (simple selection for now).
- [ ] **Backend: Implement Notification Trigger** (AC: 3)
  - [ ] Create a service method to send notifications (email or in-app).
  - [ ] Integrate `fastapi-mail` or just log the event for MVP.
  - [ ] Trigger this method upon "Accept" action.
- [ ] **Frontend: Build AI Review Layout** (AC: 1)
  - [ ] Create `AIReviewPage` component with a two-column layout (ResizablePanel or Grid).
  - [ ] Create `SuggestionList` component with virtualization if many items.
  - [ ] Create `SuggestionDetail` component with markdown rendering for rationale.
- [ ] **Frontend: Implement Review Actions** (AC: 2, 4)
  - [ ] Add "Accept" and "Reject" buttons to `SuggestionDetail`.
  - [ ] Implement API calls to update status.
  - [ ] Add "Edit" functionality (switch to input fields).
  - [ ] Implement optimistic UI updates (remove item from list immediately).
- [ ] **Frontend: BPO Selection** (AC: 3)
  - [ ] Add a User Select dropdown (filtered by BPO role) to the "Accept" flow.
- [ ] **Testing**
  - [ ] Unit test: Review endpoint status transitions and validation.
  - [ ] Integration test: Full flow of accepting a suggestion and verifying DB state.
  - [ ] Component test: Review interface renders correctly and handles actions.

## Dev Notes

- **Architecture Patterns**:
  - **Optimistic UI**: For the triage list, remove the item immediately upon click to keep the workflow fast. Revert if API fails.
  - **State Management**: Use React Query `useMutation` with `onMutate` for optimistic updates.
- **Source Tree Components**:
  - `backend/app/api/v1/endpoints/suggestions.py` (New)
  - `frontend/app/dashboard/compliance/review/` (New page)
  - `frontend/components/custom/ai-review-mode/` (New components)
- **Testing Standards**:
  - Test the state machine for suggestions strictly (cannot go from rejected back to pending without explicit action).

### Project Structure Notes

- **Alignment**:
  - Place new endpoints in `backend/app/api/v1/endpoints/`.
  - Place new UI components in `frontend/components/custom/`.
- **Conflicts**: None.

### Learnings from Previous Story

**From Story 3-2-integrate-ai-for-document-analysis-suggestion-generation (Status: ready-for-dev)**

- **New Services**: `AIService` and `Suggestion` model should be available.
- **Data Model**: Relies on the `ai_suggestions` table created in 3.2.
- **Status Flow**: This story implements the transition from `pending`.
- **Mocking**: Continue to mock external notifications if SendGrid isn't fully set up.

[Source: stories/3-2-integrate-ai-for-document-analysis-suggestion-generation.md#Dev-Agent-Record]

### References

- [Epic Tech Spec: Epic 3](docs/sprint-artifacts/tech-spec-epic-3.md)
- [Architecture Document](docs/architecture.md#6-novel-pattern-architecture-ai-review-mode)

## Dev Agent Record

### Context Reference

- docs/sprint-artifacts/3-3-build-human-in-the-loop-hitl-validation-interface.context.xml

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List