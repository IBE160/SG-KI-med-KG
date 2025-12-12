import { useQuery } from "@tanstack/react-query";
import { client } from "@/app/clientService";
import { generateGapAnalysisReport } from "@/app/openapi-client";

// Cache keys
export const GAP_ANALYSIS_KEYS = {
  report: (frameworkId: string) => ["gap-analysis", frameworkId] as const,
};

export function useGapAnalysisReport(frameworkId: string | null) {
  return useQuery({
    queryKey: GAP_ANALYSIS_KEYS.report(frameworkId || ""),
    queryFn: async () => {
      if (!frameworkId) return null;
      const response = await generateGapAnalysisReport({
        client,
        path: { framework_id: frameworkId },
      });
      return response.data;
    },
    enabled: !!frameworkId,
    staleTime: 60 * 1000, // 60s cache TTL
  });
}
