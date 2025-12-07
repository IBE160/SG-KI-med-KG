# Supabase RLS Configuration for Realtime

**Story:** 4-2-implement-real-time-status-updates
**Date:** 2025-12-07
**Status:** Documentation Complete

---

## Overview

This document describes the Row-Level Security (RLS) policies required to ensure tenant isolation for Supabase Realtime subscriptions. These policies guarantee that users from Tenant A cannot receive Realtime events for data belonging to Tenant B.

## RLS Policies Required

The following tables require RLS policies to enforce tenant isolation for Realtime:

1. `controls`
2. `risks`
3. `business_processes`

## Policy Configuration

### Controls Table

```sql
-- Enable RLS on controls table
ALTER TABLE controls ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only read controls from their tenant
CREATE POLICY "tenant_isolation_controls_select"
ON controls
FOR SELECT
USING (tenant_id = current_setting('app.current_tenant_id', TRUE)::UUID);

-- Policy: Realtime subscriptions respect tenant filtering
-- (Supabase Realtime inherits SELECT policies automatically)
```

### Risks Table

```sql
-- Enable RLS on risks table
ALTER TABLE risks ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only read risks from their tenant
CREATE POLICY "tenant_isolation_risks_select"
ON risks
FOR SELECT
USING (tenant_id = current_setting('app.current_tenant_id', TRUE)::UUID);
```

### Business Processes Table

```sql
-- Enable RLS on business_processes table
ALTER TABLE business_processes ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only read business processes from their tenant
CREATE POLICY "tenant_isolation_business_processes_select"
ON business_processes
FOR SELECT
USING (tenant_id = current_setting('app.current_tenant_id', TRUE)::UUID);
```

## How RLS Works with Supabase Realtime

1. **Subscription Filtering**: When the frontend subscribes to a Realtime channel, it includes a filter:
   ```typescript
   filter: `tenant_id=eq.${filterCriteria.tenant_id}`
   ```

2. **RLS Enforcement**: Supabase Realtime applies RLS policies automatically. Even if the filter is misconfigured or bypassed on the client side, RLS ensures that:
   - Only rows matching the user's `tenant_id` are streamed
   - Unauthorized access to other tenants' data is blocked at the database level

3. **Session Context**: The `app.current_tenant_id` setting is derived from the authenticated user's JWT claims, ensuring the correct tenant context is enforced.

## Testing RLS Policies

### Manual Test: Cross-Tenant Access Prevention

1. Log in as User A (Tenant A)
2. Open browser developer console
3. Attempt to subscribe to Realtime with Tenant B's `tenant_id`:
   ```javascript
   const channel = supabase
     .channel('test-cross-tenant')
     .on('postgres_changes', {
       event: '*',
       schema: 'public',
       table: 'controls',
       filter: 'tenant_id=eq.<tenant-b-uuid>'
     }, (payload) => {
       console.log('Received:', payload);
     })
     .subscribe();
   ```
4. Update a control in Tenant B's database
5. **Expected Result**: User A receives NO events (RLS blocks cross-tenant access)

### Automated Test (E2E)

See `frontend/e2e/realtime-tenant-isolation.spec.ts` for automated E2E test that:
- Creates users in two different tenants
- Subscribes both users to Realtime
- Updates data in Tenant B
- Verifies Tenant A user does NOT receive the event

## Verification Checklist

- [ ] RLS enabled on `controls`, `risks`, `business_processes` tables
- [ ] SELECT policies enforce `tenant_id` filtering using `app.current_tenant_id`
- [ ] Manual cross-tenant test performed and passed
- [ ] E2E test `E2E-4.3` (tenant isolation) passes
- [ ] Realtime subscriptions respect RLS (verified via logs and monitoring)

## Migration Notes

**Note**: These RLS policies are managed directly in Supabase (via Supabase Dashboard → Authentication → Policies or via SQL migrations run in Supabase SQL Editor). They are NOT part of Alembic migrations because:

1. Supabase uses PostgreSQL RLS, which is managed separately from application schema migrations
2. The `current_setting('app.current_tenant_id')` variable is set by Supabase Auth middleware based on JWT claims
3. RLS policies are enforced by PostgreSQL at the database level, independent of the backend application

**Action Required**: Run the SQL policy creation scripts in the Supabase SQL Editor for the production database.

## References

- [Supabase RLS Documentation](https://supabase.com/docs/guides/auth/row-level-security)
- [Supabase Realtime with RLS](https://supabase.com/docs/guides/realtime/postgres-changes#row-level-security)
- Architecture Document: Section 4.4 (Real-time Updates)
- Story 4.2 Acceptance Criteria: AC-4.3 (Real-Time Status Updates), AC-4.8 (Authorization and Tenant Isolation)
