# Story 4.2: Implement Real-Time Status Updates

Status: ready-for-dev

## Story

As a **user**,
I want **my dashboard to reflect live data changes without manual refresh**,
so that **I always see the current state of risks, controls, and compliance tasks**.

## Acceptance Criteria

### AC-4.3: Real-Time Status Updates

1. When a control or risk status is updated in the database, all connected dashboards reflect the change within 1 minute
2. Frontend successfully establishes Supabase Realtime subscription to `controls`, `risks`, and `business_processes` tables filtered by user's `tenant_id`
3. When a Realtime event is received, React Query cache is invalidated and dashboard metrics are refetched automatically
4. If Realtime connection fails, dashboard gracefully falls back to 60-second polling
5. Realtime connection status is visible in dashboard (connected/reconnecting indicator)

## Tasks / Subtasks

- [ ] **Frontend: Implement Supabase Realtime Subscription Hook** (AC: 4.3)
  - [ ] Create `frontend/hooks/useRealtimeSubscription.ts` custom React hook
  - [ ] Accept params: `table_name`, `filter_criteria` (e.g., tenant_id), `onEvent` callback
  - [ ] Establish Supabase Realtime channel subscription to specified table
  - [ ] Filter events by `tenant_id` using Realtime filters
  - [ ] Handle INSERT, UPDATE, DELETE events
  - [ ] Return connection status (connected, connecting, disconnected)
  - [ ] Clean up subscription on unmount
- [ ] **Frontend: Integrate Realtime into Dashboard Page** (AC: 4.3)
  - [ ] Update `frontend/app/(dashboard)/page.tsx` to use `useRealtimeSubscription` hook
  - [ ] Subscribe to `controls`, `risks`, and `business_processes` tables
  - [ ] On Realtime event, invalidate React Query cache for `/api/v1/dashboard/metrics`
  - [ ] Trigger automatic refetch of dashboard metrics
- [ ] **Frontend: Implement Fallback Polling** (AC: 4.3)
  - [ ] Detect Realtime connection failure (status = disconnected)
  - [ ] Implement 60-second interval polling as fallback using React Query's `refetchInterval`
  - [ ] Disable polling when Realtime reconnects successfully
- [ ] **Frontend: Implement Connection Status Indicator** (AC: 4.3)
  - [ ] Create `frontend/components/custom/RealtimeStatusIndicator.tsx` component
  - [ ] Display connection status: connected (green), reconnecting (yellow), disconnected (red)
  - [ ] Use badge or icon in dashboard header
  - [ ] Show tooltip with connection details on hover
- [ ] **Backend: Configure Supabase RLS for Realtime** (AC: 4.3)
  - [ ] Verify Row-Level Security (RLS) policies enforce tenant isolation for `controls`, `risks`, `business_processes` tables
  - [ ] Test Realtime subscriptions respect RLS (user from Tenant A cannot receive Tenant B events)
  - [ ] Document RLS policy configuration for Realtime
- [ ] **Testing: Unit Tests (Frontend)** (AC: 4.3)
  - [ ] Test `useRealtimeSubscription` hook establishes connection
  - [ ] Test hook calls `onEvent` callback when event received
  - [ ] Test hook cleans up subscription on unmount
  - [ ] Test RealtimeStatusIndicator displays correct status
- [ ] **Testing: Integration Tests (Frontend)** (AC: 4.3)
  - [ ] Test dashboard page establishes Realtime subscriptions to all 3 tables
  - [ ] Test React Query cache invalidation on Realtime event
  - [ ] Test fallback polling activates when Realtime disconnected
  - [ ] Test polling disables when Realtime reconnects
- [ ] **Testing: E2E Tests** (AC: 4.3)
  - [ ] E2E-4.3: Update control status in database, verify dashboard updates within 1 minute
  - [ ] Simulate Realtime connection failure, verify fallback polling activates
  - [ ] Verify connection status indicator changes (connected → disconnected → reconnecting)
  - [ ] Test tenant isolation: Tenant A user does not receive Tenant B Realtime events

## Dev Notes

### Architecture Patterns

- **Custom Hook Pattern**: Encapsulate Supabase Realtime subscription logic in `useRealtimeSubscription` hook for reusability
- **Cache Invalidation Strategy**: Use React Query's `queryClient.invalidateQueries()` to trigger refetch on Realtime events
- **Graceful Degradation**: Fallback to 60-second polling if Realtime unavailable to maintain some level of live updates
- **Connection Resilience**: Supabase client handles automatic reconnection attempts; monitor status and provide user feedback
- **Tenant Isolation**: Realtime filters ensure users only receive events for their `tenant_id` (enforced by RLS)

### Source Tree Components

**New Files:**
- `frontend/hooks/useRealtimeSubscription.ts` - Custom hook for Supabase Realtime subscriptions
- `frontend/components/custom/RealtimeStatusIndicator.tsx` - Connection status badge component

**Modified Files:**
- `frontend/app/(dashboard)/page.tsx` - Add Realtime subscriptions and cache invalidation logic
- `frontend/app/(dashboard)/layout.tsx` - Add RealtimeStatusIndicator to header

### Testing Standards

- **Frontend Unit Tests**: Test custom hook with React Testing Library, mock Supabase client
- **Frontend Integration Tests**: Test dashboard page Realtime integration with mocked Supabase Realtime channel
- **E2E Tests**: Use Playwright to simulate database changes and verify dashboard updates
- **RLS Testing**: Verify tenant isolation by attempting cross-tenant Realtime subscriptions (should fail/filter)
- **Coverage Target**: 80% code coverage for new hooks and components

### Project Structure Notes

**Alignment:**
- Frontend follows Next.js App Router structure: `frontend/app/(dashboard)/`, `frontend/components/custom/`, `frontend/hooks/`
- Consistent with architecture decisions from `docs/architecture.md`

**Conflicts:**
- None detected

### Learnings from Previous Story

**From Story 4-1-develop-role-specific-dashboards (Status: ready-for-dev)**

- **New Files to be Created** (not yet implemented, but designed in Story 4.1):
  - `backend/app/schemas/dashboard.py` - Pydantic schemas (DashboardCard, DashboardMetrics)
  - `backend/app/services/dashboard_service.py` - Dashboard metrics aggregation service
  - `backend/app/api/v1/endpoints/dashboard.py` - Dashboard API endpoint
  - `frontend/app/(dashboard)/layout.tsx` - Dashboard shell layout
  - `frontend/app/(dashboard)/page.tsx` - Main dashboard page
  - `frontend/components/custom/ActionCard.tsx` - Reusable dashboard card component
- **Modified Files** (planned): `backend/app/main.py`, `frontend/app/layout.tsx`
- **Service Pattern Established**: DashboardService with get_metrics() method following AuditService pattern
- **State Management Strategy**: React Query for server state (30-second TTL), Zustand for global state (user role, theme)
- **Performance Optimizations**: Database indexes on tenant_id/status/assigned_bpo_id, COUNT(*) queries, skeleton loading states
- **Testing Pattern**: Follow test_audit_service.py patterns - unit tests for services, integration tests for endpoints

**Relevance to This Story:**
- Story 4.2 will add Supabase Realtime to the dashboard components created in Story 4.1
- Must integrate with DashboardService and dashboard page to enable live updates
- Will subscribe to controls, risks, business_processes tables and invalidate React Query cache on changes
- React Query cache (30-second TTL from Story 4.1) will be invalidated on Realtime events for immediate updates

[Source: docs/sprint-artifacts/4-1-develop-role-specific-dashboards.md#Dev-Agent-Record]

### References

- [Tech Spec: Epic 4](docs/sprint-artifacts/tech-spec-epic-4.md#Services-and-Modules) - RealtimeSubscriptionHook specification
- [Tech Spec: Epic 4](docs/sprint-artifacts/tech-spec-epic-4.md#Data-Models-and-Contracts) - Realtime Subscription Payload (TypeScript interface)
- [Tech Spec: Epic 4](docs/sprint-artifacts/tech-spec-epic-4.md#Workflows-and-Sequencing) - Workflow 1: Dashboard Load & Real-Time Updates
- [Tech Spec: Epic 4](docs/sprint-artifacts/tech-spec-epic-4.md#NFR-Performance) - Real-Time Latency requirement (< 1 minute)
- [Tech Spec: Epic 4](docs/sprint-artifacts/tech-spec-epic-4.md#NFR-Reliability) - Graceful degradation (fallback to 60-second polling)
- [Architecture](docs/architecture.md#State-Management-Frontend) - React Query cache invalidation strategy
- [Epics](docs/epics.md#Story-4-2) - Original story definition from epic breakdown

## Dev Agent Record

### Context Reference

- docs/sprint-artifacts/4-2-implement-real-time-status-updates.context.xml

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

### Completion Notes List

### File List
