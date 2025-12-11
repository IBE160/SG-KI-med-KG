"use client";

import { createClient } from "@/lib/supabase";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

interface UpdateSuggestionStatusParams {
  suggestionId: string;
  status: "pending" | "pending_review" | "rejected";
  updatedContent?: any;
  bpoId?: string;
}

export function useUpdateSuggestionStatus() {
  const queryClient = useQueryClient();
  const supabase = createClient();

  return useMutation({
    mutationFn: async ({ suggestionId, status, updatedContent, bpoId }: UpdateSuggestionStatusParams) => {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) throw new Error("Not authenticated");

      const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      
      const response = await fetch(`${backendUrl}/api/v1/suggestions/${suggestionId}/status`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({ status, updated_content: updatedContent, bpo_id: bpoId }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to update status");
      }

      return response.json();
    },
    onMutate: async (newStatus) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ["suggestions"] });
      const previousSuggestions = queryClient.getQueryData(["suggestions"]);

      queryClient.setQueryData(["suggestions"], (old: any) => {
        // Assuming we want to remove handled items from the list or update them
        // If the list filters by "pending", then removing it is correct for optimistic UI
        return old?.filter((s: any) => s.id !== newStatus.suggestionId);
      });

      return { previousSuggestions };
    },
    onError: (err, newStatus, context) => {
      queryClient.setQueryData(["suggestions"], context?.previousSuggestions);
      toast.error(`Error: ${err.message}`);
    },
    onSuccess: () => {
      toast.success("Suggestion updated successfully");
      queryClient.invalidateQueries({ queryKey: ["suggestions"] });
    },
  });
}
