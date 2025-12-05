# Story 3.4: Implement Immutable Audit Trail

Status: ready-for-dev

## Story

As a **system**,
I want **to automatically record all critical actions (CRUD on compliance data, AI suggestion approval/rejection) in an immutable audit log**,
so that **there is a comprehensive and verifiable history for compliance audits**.

## Acceptance Criteria

1. **`audit_logs` table captures CREATE/UPDATE/DELETE on Risks/Controls.**
    - Any creation, modification, or deletion of a Risk or Control entity triggers the creation of an audit log entry.
    - The entry includes the type of entity (Risk/Control), the entity ID, and the type of action (CREATE/UPDATE/DELETE).
2. **Captures "Approve Suggestion" actions.**
    - When an AI suggestion is approved (promoted to Risk/Control), an audit log entry is created.
    - The action is clearly logged as "APPROVE_SUGGESTION" (or similar).
3. **Log entry includes Actor, Timestamp, Action, and Diff.**
    - Each log entry records the UUID of the user who performed the action (`actor_id`).
    - A precise timestamp (`created_at`) is recorded.
    - For updates, a JSON diff of the changes (old values vs. new values) is stored in the `changes` column.
    - For creates/deletes, the full state or relevant ID is captured.
4. **Logs are immutable (enforced by DB policy or application logic).**
    - The `audit_logs` table is append-only.
    - No API endpoints exist to update or delete audit log entries.
    - (Optional but recommended) Row Level Security (RLS) prevents updates/deletes even by standard users.

## Tasks / Subtasks

- [ ] **Backend: Implement Audit Log Data Model** (AC: 1, 3)
  - [ ] Define `AuditLog` SQLAlchemy model in `backend/app/models/audit_log.py`.
  - [ ] Create Alembic migration for `audit_logs` table (with fields: id, action, entity_type, entity_id, actor_id, changes, timestamp).
  - [ ] Define Pydantic schemas in `backend/app/schemas/audit_log.py` (Read only).
- [ ] **Backend: Implement Audit Service** (AC: 1, 2, 3)
  - [ ] Create `backend/app/services/audit_service.py`.
  - [ ] Implement `log_action(db, actor_id, action, entity_type, entity_id, changes)` method.
  - [ ] Implement helper to calculate JSON diff between two model states.
- [ ] **Backend: Integrate Audit Logging into Services** (AC: 1, 2)
  - [ ] Update `RiskService` / `ControlService` (or CRUD endpoints) to call `log_action` on changes.
  - [ ] Update `SuggestionService` (from Story 3.3) to call `log_action` on approval.
- [ ] **Backend: Audit Log Retrieval Endpoint**
  - [ ] Implement `GET /api/v1/audit-logs` endpoint (filtered by tenant, entity, actor).
  - [ ] Ensure pagination support.
- [ ] **Database: Enforce Immutability (Optional/Advanced)** (AC: 4)
  - [ ] Add a Postgres trigger or RLS policy to raise error on UPDATE/DELETE for `audit_logs`.
- [ ] **Testing**
  - [ ] Unit test: Diff calculation logic.
  - [ ] Integration test: Create a Risk and verify `audit_logs` entry is created.
  - [ ] Integration test: Update a Control and verify `changes` JSON diff.
  - [ ] Integration test: Approve suggestion and verify log.

## Dev Notes

- **Architecture Patterns**:
  - **Service Layer**: Centralize the logging logic in `AuditService` to avoid code duplication in every CRUD handler.
  - **JSON Diff**: Store only the changed fields for updates to save space and improve readability.
- **Source Tree Components**:
  - `backend/app/models/audit_log.py` (New)
  - `backend/app/schemas/audit_log.py` (New)
  - `backend/app/services/audit_service.py` (New)
  - `backend/app/api/v1/endpoints/audit_logs.py` (New)
- **Testing Standards**:
  - Verify the *content* of the log entry, not just its existence. Check that `actor_id` matches the current user.

### Project Structure Notes

- **Alignment**:
  - Standard backend structure.
- **Conflicts**: None.

### Learnings from Previous Story

**From Story 3-3-build-human-in-the-loop-hitl-validation-interface (Status: ready-for-dev)**

- **Integration Point**: This story needs to hook into the `PATCH` endpoint created in Story 3.3 to log the "Accept" action.
- **Data Model**: Will reference `User` (actor) and the entities (Risk/Control/Suggestion).
- **Pattern**: The service pattern is established.

[Source: stories/3-3-build-human-in-the-loop-hitl-validation-interface.md#Dev-Agent-Record]

### References

- [Epic Tech Spec: Epic 3](docs/sprint-artifacts/tech-spec-epic-3.md)
- [PRD: Functional Requirements](docs/PRD.md#5-audit--history)

## Dev Agent Record

### Context Reference

- docs/sprint-artifacts/3-4-implement-immutable-audit-trail.context.xml

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
