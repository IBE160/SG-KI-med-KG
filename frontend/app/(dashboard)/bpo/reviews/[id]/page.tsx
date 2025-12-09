"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { ArrowLeft, Check, X, Edit2, AlertTriangle, ExternalLink } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";

import {
  assessmentsGetSuggestionDetail,
  assessmentsSubmitAssessment,
  SuggestionDetailResponse,
  AssessmentAction,
  ResidualRisk,
} from "@/app/clientService";

// Form schema
const formSchema = z.object({
  business_process_name: z.string().min(1, "Business Process Name is required"),
  risk_description: z.string().min(1, "Risk Description is required"),
  control_description: z.string().min(1, "Control Description is required"),
  residual_risk: z.enum(["low", "medium", "high"]).optional(),
});

type FormValues = z.infer<typeof formSchema>;

export default function BPOReviewDetailPage() {
  const router = useRouter();
  const params = useParams();
  const suggestionId = params.id as string;
  const queryClient = useQueryClient();

  const [isEditing, setIsEditing] = useState(false);
  const [showDiscardDialog, setShowDiscardDialog] = useState(false);

  // Fetch suggestion details
  const { data: suggestion, isLoading, error } = useQuery<SuggestionDetailResponse>({
    queryKey: ["/api/v1/assessments", suggestionId],
    queryFn: async () => {
      const response = await assessmentsGetSuggestionDetail({
        path: { suggestion_id: suggestionId },
      });
      if (response.error) {
        throw new Error((response.error.detail as unknown as string) || "Failed to fetch suggestion details");
      }
      return response.data!;
    },
    enabled: !!suggestionId,
  });

  // Initialize form
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      business_process_name: "",
      risk_description: "",
      control_description: "",
      residual_risk: undefined,
    },
  });

  // Update form values when data is loaded
  useEffect(() => {
    if (suggestion) {
      form.reset({
        business_process_name: suggestion.business_process_name,
        risk_description: suggestion.risk_description,
        control_description: suggestion.control_description,
        residual_risk: undefined, // Always start undefined, must be selected
      });
    }
  }, [suggestion, form.reset]);

  // Assessment mutation
  const assessmentMutation = useMutation({
    mutationFn: async (data: { action: AssessmentAction; residual_risk?: ResidualRisk; edits?: Partial<FormValues> }) => {
      const response = await assessmentsSubmitAssessment({
        path: { suggestion_id: suggestionId },
        body: {
          action: data.action,
          residual_risk: data.residual_risk,
          edited_business_process: data.edits?.business_process_name,
          edited_risk_description: data.edits?.risk_description,
          edited_control_description: data.edits?.control_description,
        },
      });

      if (response.error) {
        throw new Error((response.error.detail as unknown as string) || "Failed to submit assessment");
      }
      return response.data;
    },
    onSuccess: (data, variables) => {
      if (variables.action === "approve") {
        toast.success("✅ Successfully added to register", {
          description: "Active records have been created.",
          action: {
            label: "View",
            onClick: () => router.push("/dashboard/controls"), // Navigate to controls list or specific item if possible
          },
        });
      } else {
        toast.info("🗑️ Item discarded", {
          description: "Suggestion has been archived.",
        });
      }
      // Invalidate queries to refresh list
      queryClient.invalidateQueries({ queryKey: ["/api/v1/assessments/pending"] });
      router.push("/dashboard/bpo/reviews");
    },
    onError: (error: Error) => {
      toast.error("Error submitting assessment", {
        description: error.message,
      });
    },
  });

  const onApprove = (values: FormValues) => {
    if (!values.residual_risk) {
      form.setError("residual_risk", {
        type: "manual",
        message: "Residual risk must be selected before approving",
      });
      return;
    }

    // Check for edits by comparing with original suggestion
    const edits: Partial<FormValues> = {};
    if (values.business_process_name !== suggestion?.business_process_name) {
      edits.business_process_name = values.business_process_name;
    }
    if (values.risk_description !== suggestion?.risk_description) {
      edits.risk_description = values.risk_description;
    }
    if (values.control_description !== suggestion?.control_description) {
      edits.control_description = values.control_description;
    }

    assessmentMutation.mutate({
      action: "approve",
      residual_risk: values.residual_risk as ResidualRisk,
      edits: Object.keys(edits).length > 0 ? edits : undefined,
    });
  };

  const onDiscard = () => {
    assessmentMutation.mutate({
      action: "discard",
    });
    setShowDiscardDialog(false);
  };

  if (isLoading) {
    return (
      <div className="p-8 space-y-6">
        <Skeleton className="h-8 w-1/3" />
        <Skeleton className="h-[600px] w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="p-4 border border-red-500 bg-red-50 text-red-900 rounded flex items-center gap-2">
          <AlertTriangle className="h-5 w-5" />
          <span>{error instanceof Error ? error.message : "Failed to load suggestion"}</span>
        </div>
        <Button variant="outline" className="mt-4" onClick={() => router.push("/dashboard/bpo/reviews")}>
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Pending Reviews
        </Button>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.push("/dashboard/bpo/reviews")}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="text-2xl font-bold">Review Suggestion</h1>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
            Pending Review
          </Badge>
          <span className="text-sm text-gray-500">
            Created: {suggestion && new Date(suggestion.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-lg font-medium">Suggestion Details</CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsEditing(!isEditing)}
                className={isEditing ? "bg-blue-50 text-blue-600" : ""}
              >
                <Edit2 className="h-4 w-4 mr-2" />
                {isEditing ? "Editing..." : "Edit"}
              </Button>
            </CardHeader>
            <CardContent className="pt-4">
              <Form {...form}>
                <form className="space-y-6">
                  {/* Read-only fields context */}
                  <div className="grid grid-cols-2 gap-4 bg-gray-50 p-4 rounded-lg">
                    <div>
                      <span className="text-xs font-semibold text-gray-500 uppercase">Risk Name</span>
                      <p className="font-medium mt-1">{suggestion?.risk_name}</p>
                    </div>
                    <div>
                      <span className="text-xs font-semibold text-gray-500 uppercase">Control Name</span>
                      <p className="font-medium mt-1">{suggestion?.control_name}</p>
                    </div>
                  </div>

                  <FormField
                    control={form.control}
                    name="business_process_name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Business Process</FormLabel>
                        <FormControl>
                          <Input {...field} disabled={!isEditing} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="risk_description"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Risk Description</FormLabel>
                        <FormControl>
                          <Textarea {...field} disabled={!isEditing} className="min-h-[100px]" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="control_description"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Control Description</FormLabel>
                        <FormControl>
                          <Textarea {...field} disabled={!isEditing} className="min-h-[100px]" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {suggestion?.source_reference && (
                    <div className="pt-2">
                      <FormLabel className="mb-2 block">Source Reference</FormLabel>
                      <a
                        href={suggestion.source_reference}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center text-sm text-blue-600 hover:underline"
                      >
                        <ExternalLink className="h-3 w-3 mr-1" />
                        {suggestion.source_reference}
                      </a>
                    </div>
                  )}
                </form>
              </Form>
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-1 space-y-6">
          <Card className="bg-gray-50 border-blue-100">
            <CardHeader>
              <CardTitle className="text-md">AI Rationale</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-700 leading-relaxed">
                {suggestion?.rationale}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-md">Assessment Decision</CardTitle>
              <CardDescription>Select residual risk to approve</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Form {...form}>
                <FormField
                  control={form.control}
                  name="residual_risk"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Residual Risk <span className="text-red-500">*</span></FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select level" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="low">Low</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="high">High</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </Form>
            </CardContent>
            <CardFooter className="flex-col gap-3">
              <Button
                className="w-full bg-green-600 hover:bg-green-700"
                onClick={form.handleSubmit(onApprove)}
                disabled={assessmentMutation.isPending}
              >
                {assessmentMutation.isPending && assessmentMutation.variables?.action === "approve" ? (
                  "Approving..."
                ) : (
                  <>
                    <Check className="mr-2 h-4 w-4" /> Approve & Add to Register
                  </>
                )}
              </Button>
              <Button
                variant="destructive"
                className="w-full"
                onClick={() => setShowDiscardDialog(true)}
                disabled={assessmentMutation.isPending}
              >
                <X className="mr-2 h-4 w-4" /> Discard Suggestion
              </Button>
            </CardFooter>
          </Card>
        </div>
      </div>

      <AlertDialog open={showDiscardDialog} onOpenChange={setShowDiscardDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action will discard the AI suggestion and archive it. This cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={onDiscard}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              {assessmentMutation.isPending && assessmentMutation.variables?.action === "discard" ? (
                "Discarding..."
              ) : (
                "Yes, Discard"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}