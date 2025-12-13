import { useQuery } from "@tanstack/react-query";
import { client } from "@/app/clientService";

// Cache keys
export const GAP_ANALYSIS_KEYS = {
  report: (frameworkId: string) => ["gap-analysis", frameworkId] as const,
};

// Type definition for Gap Analysis Report
export interface GapAnalysisReport {
  framework_id: string;
  framework_name: string;
  total_requirements: number;
  mapped_requirements: number;
  unmapped_requirements: number;
  coverage_percentage: number;
  gaps: Array<{
    requirement_id: string;
    requirement_name: string;
    requirement_description: string;
  }>;
}

export function useGapAnalysisReport(frameworkId: string | null) {
  return useQuery({
    queryKey: GAP_ANALYSIS_KEYS.report(frameworkId || ""),
    queryFn: async () => {
      if (!frameworkId) return null;
      // Direct API call since the endpoint isn't in the generated SDK yet
      const response = await client.get<GapAnalysisReport>({
        url: `/api/v1/reports/gap-analysis/${frameworkId}`,
      });
      return response.data;
    },
    enabled: !!frameworkId,
    staleTime: 60 * 1000, // 60s cache TTL
  });
}
