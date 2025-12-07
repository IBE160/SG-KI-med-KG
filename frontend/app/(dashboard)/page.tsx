"use client";

import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtimeSubscription } from "@/hooks/useRealtimeSubscription";
import { RealtimeStatusIndicator } from "@/components/custom/RealtimeStatusIndicator";

// This is a demo implementation showing Realtime integration pattern.
// Will be replaced/integrated when Story 4.1 dashboard components are merged.

export default function DashboardPage() {
  const queryClient = useQueryClient();
  const [tenantId, setTenantId] = useState<string>("");

  // In production, get tenant_id from authenticated user session
  useEffect(() => {
    // Placeholder: Would normally fetch from user session/JWT
    setTenantId("demo-tenant-id");
  }, []);

  // Subscribe to controls table changes
  const controlsSubscription = useRealtimeSubscription({
    tableName: "controls",
    filterCriteria: { tenant_id: tenantId },
    onEvent: (change) => {
      console.log("Controls changed:", change);
      // Invalidate React Query cache for dashboard metrics
      queryClient.invalidateQueries({ queryKey: ["/api/v1/dashboard/metrics"] });
    },
    enabled: !!tenantId,
  });

  // Subscribe to risks table changes
  const risksSubscription = useRealtimeSubscription({
    tableName: "risks",
    filterCriteria: { tenant_id: tenantId },
    onEvent: (change) => {
      console.log("Risks changed:", change);
      queryClient.invalidateQueries({ queryKey: ["/api/v1/dashboard/metrics"] });
    },
    enabled: !!tenantId,
  });

  // Subscribe to business_processes table changes
  const processesSubscription = useRealtimeSubscription({
    tableName: "business_processes",
    filterCriteria: { tenant_id: tenantId },
    onEvent: (change) => {
      console.log("Business processes changed:", change);
      queryClient.invalidateQueries({ queryKey: ["/api/v1/dashboard/metrics"] });
    },
    enabled: !!tenantId,
  });

  // Determine overall connection status (use worst case)
  const overallStatus =
    controlsSubscription.status === "disconnected" ||
    risksSubscription.status === "disconnected" ||
    processesSubscription.status === "disconnected"
      ? "disconnected"
      : controlsSubscription.status === "connecting" ||
        risksSubscription.status === "connecting" ||
        processesSubscription.status === "connecting"
      ? "connecting"
      : "connected";

  // Fallback polling: When Realtime disconnected, poll every 60 seconds
  // This query would normally fetch dashboard metrics from /api/v1/dashboard/metrics
  const { data: dashboardMetrics } = useQuery({
    queryKey: ["/api/v1/dashboard/metrics"],
    queryFn: async () => {
      // Placeholder: In production, would call actual backend API
      console.log("Polling dashboard metrics (fallback mode)");
      return { polledAt: new Date().toISOString() };
    },
    refetchInterval: overallStatus === "disconnected" ? 60000 : false, // 60s when disconnected
    enabled: !!tenantId,
  });

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <RealtimeStatusIndicator status={overallStatus} />
      </div>

      <div className="space-y-4">
        <div className="p-4 border rounded-lg">
          <h2 className="font-semibold mb-2">Real-time Subscriptions Status</h2>
          <ul className="space-y-2 text-sm">
            <li>
              Controls: <span className="font-mono">{controlsSubscription.status}</span>
            </li>
            <li>
              Risks: <span className="font-mono">{risksSubscription.status}</span>
            </li>
            <li>
              Business Processes: <span className="font-mono">{processesSubscription.status}</span>
            </li>
          </ul>
        </div>

        <div className="p-4 border rounded-lg bg-blue-50">
          <h3 className="font-semibold text-blue-900 mb-2">Integration Notes (Story 4.2)</h3>
          <p className="text-sm text-blue-800">
            This demo page shows the Realtime integration pattern. When Story 4.1 dashboard
            components are merged, this will be replaced with the actual role-specific dashboard
            that includes ActionCards and metrics from the backend API.
          </p>
          <p className="text-sm text-blue-800 mt-2">
            The Realtime subscriptions are active and will invalidate the React Query cache
            for dashboard metrics when database changes occur, triggering automatic refetch.
          </p>
          <p className="text-sm text-blue-800 mt-2">
            <strong>Fallback polling:</strong> When Realtime status is &quot;disconnected&quot;, the dashboard
            automatically enables 60-second polling as a graceful degradation strategy.
            {overallStatus === "disconnected" && (
              <span className="block mt-1 font-semibold">
                ⚠️ Fallback polling is currently ACTIVE
              </span>
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
