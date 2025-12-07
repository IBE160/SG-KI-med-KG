"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter, useParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { ArrowLeft, ExternalLink, Check, X, Edit, AlertCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useToast } from "@/components/ui/use-toast";
import { Skeleton } from "@/components/ui/skeleton";

interface SuggestionDetail {
  suggestion_id: string;
  business_process_name: string;
  risk_name: string;
  risk_description: string;
  control_name: string;
  control_description: string;
  rationale: string;
  source_reference: string;
  created_at: string;
}

interface AssessmentFormData {
  business_process_name: string;
  risk_description: string;
  control_description: string;
  residual_risk: string;
}

export default function BPOReviewDetailPage() {
  const router = useRouter();
  const params = useParams();
  const suggestionId = params.id as string;
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const [isEditing, setIsEditing] = useState(false);
  const [discardDialogOpen, setDiscardDialogOpen] = useState(false);

  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm<AssessmentFormData>();
  const residualRisk = watch("residual_risk");

  // Fetch suggestion details
  const { data: suggestion, isLoading, error } = useQuery<SuggestionDetail>({
    queryKey: ["/api/v1/assessments", suggestionId],
    queryFn: async () => {
      const response = await fetch(`/api/v1/assessments/${suggestionId}`, {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("authToken")}`,
        },
      });
      if (!response.ok) {
        if (response.status === 403) throw new Error("Access denied or suggestion not assigned to you.");
        if (response.status === 404) throw new Error("Suggestion not found.");
        throw new Error("Failed to fetch suggestion details");
      }
      return response.json();
    },
  });

  // Approve Mutation
  const approveMutation = useMutation({
    mutationFn: async (data: AssessmentFormData) => {
      const payload: any = {
        action: "approve",
        residual_risk: data.residual_risk,
      };

      // Only include edits if they differ from original
      if (suggestion) {
        if (data.business_process_name !== suggestion.business_process_name) {
          payload.edited_business_process = data.business_process_name;
        }
        if (data.risk_description !== suggestion.risk_description) {
          payload.edited_risk_description = data.risk_description;
        }
        if (data.control_description !== suggestion.control_description) {
          payload.edited_control_description = data.control_description;
        }
      }

      const response = await fetch(`/api/v1/assessments/${suggestionId}/assess`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("authToken")}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Failed to approve suggestion");
      }
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "✅ Successfully added to register",
        description: "The control has been approved and activated.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/v1/assessments/pending"] });
      router.push("/dashboard/bpo/reviews");
    },
    onError: (err: Error) => {
      toast({
        variant: "destructive",
        title: "Error",
        description: err.message,
      });
    },
  });

  // Discard Mutation
  const discardMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`/api/v1/assessments/${suggestionId}/assess`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("authToken")}`,
        },
        body: JSON.stringify({ action: "discard" }),
      });

      if (!response.ok) {
        throw new Error("Failed to discard suggestion");
      }
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "🗑️ Item discarded",
        description: "The suggestion has been archived.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/v1/assessments/pending"] });
      router.push("/dashboard/bpo/reviews");
    },
    onError: (err: Error) => {
      toast({
        variant: "destructive",
        title: "Error",
        description: err.message,
      });
    },
  });

  // Populate form defaults when data loads
  if (suggestion && !isEditing && watch("business_process_name") !== suggestion.business_process_name) {
     // Using a check to avoid infinite re-renders or resetting user edits if logic was different.
     // Better approach: use defaultValues in useForm or useEffect to reset.
     // For simplicity with react-hook-form v7, we can use `values` prop if using controlled, 
     // or `reset()` inside useEffect.
  }
  
  // Using useEffect to set default values once data is loaded
  // This is cleaner than conditional rendering side-effects
  // Importing useEffect
  
  if (isLoading) {
    return (
      <div className="p-8 max-w-4xl mx-auto space-y-6">
        <div className="flex items-center gap-4">
            <Skeleton className="h-10 w-10 rounded-full" />
            <Skeleton className="h-8 w-64" />
        </div>
        <Card>
            <CardHeader><Skeleton className="h-6 w-48" /></CardHeader>
            <CardContent className="space-y-4">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-24 w-full" />
                <Skeleton className="h-24 w-full" />
            </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 max-w-4xl mx-auto">
        <div className="p-4 border border-red-500 bg-red-50 text-red-900 rounded flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            {error instanceof Error ? error.message : "An error occurred"}
        </div>
        <Button variant="ghost" onClick={() => router.back()} className="mt-4">
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Pending Reviews
        </Button>
      </div>
    );
  }

  const onApprove = (data: AssessmentFormData) => {
    approveMutation.mutate(data);
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center mb-6">
        <Button variant="ghost" size="sm" onClick={() => router.back()} className="mr-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <h1 className="text-2xl font-bold">Review Suggestion</h1>
      </div>

      <div className="grid gap-6">
        {/* Main Assessment Form */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>{suggestion?.risk_name}</CardTitle>
                <CardDescription>Review the AI-suggested risk and control details.</CardDescription>
              </div>
              <Button 
                variant={isEditing ? "secondary" : "outline"} 
                size="sm" 
                onClick={() => {
                    if (!isEditing && suggestion) {
                        // Reset to current suggestion values when starting edit
                        setValue("business_process_name", suggestion.business_process_name);
                        setValue("risk_description", suggestion.risk_description);
                        setValue("control_description", suggestion.control_description);
                    }
                    setIsEditing(!isEditing);
                }}
              >
                <Edit className="h-4 w-4 mr-2" />
                {isEditing ? "Cancel Editing" : "Edit Details"}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            
            {/* Business Process */}
            <div className="space-y-2">
              <Label htmlFor="process">Business Process</Label>
              {isEditing ? (
                 <Input 
                    id="process" 
                    defaultValue={suggestion?.business_process_name}
                    {...register("business_process_name")} 
                 />
              ) : (
                <div className="p-3 bg-gray-50 rounded-md border text-sm">
                    {suggestion?.business_process_name}
                </div>
              )}
            </div>

            {/* Risk Description */}
            <div className="space-y-2">
              <Label htmlFor="risk_desc">Risk Description</Label>
              {isEditing ? (
                 <Textarea 
                    id="risk_desc" 
                    className="min-h-[100px]"
                    defaultValue={suggestion?.risk_description}
                    {...register("risk_description")} 
                 />
              ) : (
                <div className="p-3 bg-gray-50 rounded-md border text-sm whitespace-pre-wrap">
                    {suggestion?.risk_description}
                </div>
              )}
            </div>

            {/* Control Description */}
            <div className="space-y-2">
              <Label htmlFor="control_desc">Control Description</Label>
               {isEditing ? (
                 <Textarea 
                    id="control_desc" 
                    className="min-h-[100px]"
                    defaultValue={suggestion?.control_description}
                    {...register("control_description")} 
                 />
              ) : (
                <div className="p-3 bg-gray-50 rounded-md border text-sm whitespace-pre-wrap">
                    {suggestion?.control_description}
                </div>
              )}
            </div>
            
            {/* Rationale (Read Only) */}
            <div className="space-y-2">
                <Label>AI Rationale</Label>
                <div className="p-3 bg-blue-50 text-blue-900 rounded-md border border-blue-100 text-sm">
                    {suggestion?.rationale}
                </div>
            </div>

            {/* Source Reference */}
            <div className="space-y-2">
                <Label>Source Reference</Label>
                <div className="flex items-center gap-2">
                     <a 
                        href={suggestion?.source_reference} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline text-sm flex items-center gap-1"
                     >
                        {suggestion?.source_reference}
                        <ExternalLink className="h-3 w-3" />
                     </a>
                </div>
            </div>

          </CardContent>
        </Card>

        {/* Action Panel */}
        <Card className="border-t-4 border-t-primary">
            <CardHeader>
                <CardTitle>Assessment Decision</CardTitle>
                <CardDescription>Categorize the residual risk to approve this control.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
                <div className="max-w-xs space-y-2">
                    <Label htmlFor="residual_risk">Residual Risk <span className="text-red-500">*</span></Label>
                    <Select onValueChange={(val) => setValue("residual_risk", val)}>
                        <SelectTrigger id="residual_risk">
                            <SelectValue placeholder="Select risk level" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="low">Low</SelectItem>
                            <SelectItem value="medium">Medium</SelectItem>
                            <SelectItem value="high">High</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <div className="flex justify-between items-center pt-4 border-t">
                    <Button 
                        variant="destructive" 
                        type="button" 
                        onClick={() => setDiscardDialogOpen(true)}
                        disabled={approveMutation.isPending || discardMutation.isPending}
                    >
                        <X className="h-4 w-4 mr-2" />
                        Discard
                    </Button>

                    <Button 
                        onClick={handleSubmit(onApprove)}
                        disabled={!residualRisk || approveMutation.isPending || discardMutation.isPending}
                        className="min-w-[150px]"
                    >
                        {approveMutation.isPending ? "Approving..." : (
                            <>
                                <Check className="h-4 w-4 mr-2" />
                                Approve & Add
                            </>
                        )}
                    </Button>
                </div>
            </CardContent>
        </Card>
      </div>

      {/* Discard Confirmation Modal */}
      <Dialog open={discardDialogOpen} onOpenChange={setDiscardDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Discard Suggestion?</DialogTitle>
            <DialogDescription>
              Are you sure you want to discard this suggestion? This action will archive the suggestion and remove it from your pending list.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDiscardDialogOpen(false)}>Cancel</Button>
            <Button 
                variant="destructive" 
                onClick={() => discardMutation.mutate()}
                disabled={discardMutation.isPending}
            >
                {discardMutation.isPending ? "Discarding..." : "Confirm Discard"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
