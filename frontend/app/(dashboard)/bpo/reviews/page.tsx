"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { assessmentsGetPendingReviews, PendingReviewsResponse } from "@/app/clientService";

export default function BPOPendingReviewsPage() {
  const router = useRouter();

  // Fetch pending reviews from API
  const { data, isLoading, error } = useQuery<PendingReviewsResponse>({
    queryKey: ["/api/v1/assessments/pending"],
    queryFn: async () => {
      const response = await assessmentsGetPendingReviews({
        query: {
          page: 1,
          size: 20,
        },
      });
      if (response.error) {
        throw new Error("Failed to fetch pending reviews");
      }
      return response.data;
    },
  });

  const handleRowClick = (suggestionId: string) => {
    router.push(`/dashboard/bpo/reviews/${suggestionId}`);
  };

  if (isLoading) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-6">Pending Reviews</h1>
        <div className="space-y-4">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-6">Pending Reviews</h1>
        <div className="p-4 border border-red-500 bg-red-50 text-red-900 rounded">
          {error instanceof Error ? error.message : "An error occurred"}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Pending Reviews</h1>
        <span className="text-sm text-gray-600">
          {data?.total || 0} total items
        </span>
      </div>

      {data && data.items.length > 0 ? (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Business Process</TableHead>
              <TableHead>Risk</TableHead>
              <TableHead>Control</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.items.map((item) => (
              <TableRow
                key={item.suggestion_id}
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => handleRowClick(item.suggestion_id)}
              >
                <TableCell className="font-medium">{item.business_process_name}</TableCell>
                <TableCell>{item.risk_name}</TableCell>
                <TableCell>{item.control_name}</TableCell>
                <TableCell className="text-sm text-gray-600">
                  {new Date(item.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRowClick(item.suggestion_id);
                    }}
                  >
                    Review
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      ) : (
        <div className="p-8 text-center text-gray-600">
          No pending reviews. All caught up!
        </div>
      )}

      {/* TODO: Add pagination controls when needed */}
    </div>
  );
}
