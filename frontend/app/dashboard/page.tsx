"use client";

import { useQuery } from "@tanstack/react-query";
import { ActionCard } from "@/components/custom/ActionCard";
import { useRole } from "@/lib/role";
import { createClient } from "@/lib/supabase";

interface DashboardCard {
  card_id: string;
  title: string;
  metric: number;
  metric_label: string;
  icon: string;
  action_link: string;
  status?: string | null;
}

interface DashboardMetrics {
  user_role: string;
  cards: DashboardCard[];
}

async function fetchDashboardMetrics(accessToken: string): Promise<DashboardMetrics> {
  const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
  const response = await fetch(`${backendUrl}/api/v1/dashboard/metrics`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    mode: "cors",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch dashboard metrics: ${response.statusText}`);
  }

  return response.json();
}

export default function DashboardPage() {
  const { role, loading: roleLoading } = useRole();
  const supabase = createClient();

  const { data: metricsData, isLoading: metricsLoading, error } = useQuery({
    queryKey: ["dashboardMetrics"],
    queryFn: async () => {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session?.access_token) {
        throw new Error("No access token available");
      }

      return fetchDashboardMetrics(session.access_token);
    },
    // Refetch every 30 seconds for real-time data
    refetchInterval: 30000,
    enabled: !!role && !roleLoading,
  });

  if (roleLoading || metricsLoading) {
    return (
      <div>
        <h2 className="text-2xl font-semibold mb-6">Dashboard</h2>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <ActionCard
            title="Loading..."
            metric={0}
            metricLabel=""
            icon="Activity"
            actionLink="#"
            loading={true}
          />
          <ActionCard
            title="Loading..."
            metric={0}
            metricLabel=""
            icon="Activity"
            actionLink="#"
            loading={true}
          />
          <ActionCard
            title="Loading..."
            metric={0}
            metricLabel=""
            icon="Activity"
            actionLink="#"
            loading={true}
          />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <h2 className="text-2xl font-semibold mb-6">Dashboard</h2>
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">
            Failed to load dashboard metrics. Please try refreshing the page.
          </p>
          <p className="text-sm text-red-600 mt-2">{(error as Error).message}</p>
        </div>
      </div>
    );
  }

  const roleLabels: Record<string, string> = {
    admin: "Administrator",
    bpo: "Business Process Owner",
    compliance_officer: "Compliance Officer",
    executive: "Executive",
    general: "User",
  };

  const roleLabel = roleLabels[role || "general"] || "User";

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-semibold">Dashboard</h2>
        <p className="text-muted-foreground">
          Welcome, {roleLabel}. Here's your personalized overview.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {metricsData?.cards.map((card) => (
          <ActionCard
            key={card.card_id}
            title={card.title}
            metric={card.metric}
            metricLabel={card.metric_label}
            icon={card.icon}
            actionLink={card.action_link}
            status={card.status as "urgent" | "normal" | null}
          />
        ))}
      </div>

      {(!metricsData?.cards || metricsData.cards.length === 0) && (
        <div className="p-8 bg-muted rounded-lg text-center">
          <p className="text-muted-foreground">No dashboard cards available for your role.</p>
        </div>
      )}
    </div>
  );
}
