"use client";

import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { createClient } from "@/lib/supabase";
import { SuggestionList } from "@/components/custom/ai-review-mode/SuggestionList";
import { SuggestionDetail } from "@/components/custom/ai-review-mode/SuggestionDetail";
import { useUpdateSuggestionStatus } from "@/components/custom/ai-review-mode/useSuggestionMutation";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";

export default function AIReviewPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const supabase = createClient();
  
  // Fetch suggestions
  const { data: suggestions, isLoading } = useQuery({
    queryKey: ["suggestions"],
    queryFn: async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) return [];
      
      const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/v1/suggestions?status=pending`, {
        headers: { Authorization: `Bearer ${session.access_token}` },
      });
      if (!response.ok) throw new Error("Failed to fetch suggestions");
      return response.json();
    },
  });

  // Fetch BPO users
  const { data: bpoUsers } = useQuery({
    queryKey: ["users", "bpo"],
    queryFn: async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) return [];
      
      const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/v1/users?role=bpo`, {
        headers: { Authorization: `Bearer ${session.access_token}` },
      });
      if (!response.ok) throw new Error("Failed to fetch BPO users");
      return response.json();
    },
  });

  const updateStatus = useUpdateSuggestionStatus();

  // Auto-select first item
  useEffect(() => {
    if (suggestions?.length && !selectedId) {
      setSelectedId(suggestions[0].id);
    }
  }, [suggestions, selectedId]);

  const selectedSuggestion = suggestions?.find((s: any) => s.id === selectedId);

  const handleAccept = (updatedContent?: any, bpoId?: string) => {
    if (!selectedId) return;
    
    updateStatus.mutate({ 
      suggestionId: selectedId, 
      status: "pending_review", 
      updatedContent, 
      bpoId 
    });

    // Optimistic selection of next
    const currentIndex = suggestions?.findIndex((s: any) => s.id === selectedId) || 0;
    const next = suggestions?.[currentIndex + 1] || suggestions?.[0];
    if (next) setSelectedId(next.id);
  };

  const handleReject = () => {
    if (!selectedId) return;
    updateStatus.mutate({ suggestionId: selectedId, status: "rejected" });
    // Optimistic selection of next
    const currentIndex = suggestions?.findIndex((s: any) => s.id === selectedId) || 0;
    const next = suggestions?.[currentIndex + 1] || suggestions?.[0];
    if (next) setSelectedId(next.id);
  };

  return (
    <div className="h-[calc(100vh-4rem)] w-full border rounded-lg overflow-hidden bg-background">
      <ResizablePanelGroup direction="horizontal">
        <ResizablePanel defaultSize={30} minSize={20}>
          <div className="h-full flex flex-col">
            <div className="p-4 border-b font-semibold bg-muted/50">
              Pending Suggestions ({suggestions?.length || 0})
            </div>
            {isLoading ? (
              <div className="p-4">Loading...</div>
            ) : (
              <SuggestionList 
                suggestions={suggestions || []} 
                selectedId={selectedId} 
                onSelect={setSelectedId} 
              />
            )}
          </div>
        </ResizablePanel>
        
        <ResizableHandle />
        
        <ResizablePanel defaultSize={70}>
          <SuggestionDetail 
            suggestion={selectedSuggestion} 
            bpoUsers={bpoUsers || []}
            onAccept={handleAccept} 
            onReject={handleReject} 
          />
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
}
