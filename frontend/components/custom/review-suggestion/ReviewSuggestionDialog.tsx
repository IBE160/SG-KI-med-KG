"use client";

import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
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
import { AISuggestionRead } from "@/app/openapi-client/types.gen";
import { createClient } from "@/lib/supabase";

interface User {
  id: string;
  full_name: string | null;
  email: string;
  roles: string[];
  tenant_id: string;
}

const formSchemaWithBPO = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().optional(),
  rationale: z.string().optional(),
  bpoId: z.union([z.string().uuid(), z.literal("")]), // Allow empty string or valid UUID
});

const formSchemaWithoutBPO = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().optional(),
  rationale: z.string().optional(),
});

interface ReviewSuggestionDialogProps {
  suggestion: AISuggestionRead;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void; // Callback to refresh parent list
}

import { Badge } from "@/components/ui/badge";
import { AlertCircle, Shield, Briefcase } from "lucide-react";

// ... existing imports

export function ReviewSuggestionDialog({
  suggestion,
  isOpen,
  onOpenChange,
  onSuccess,
}: ReviewSuggestionDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [bpos, setBpos] = useState<User[]>([]);

  const isPendingReview = suggestion.status === "pending_review";
  const formSchema = isPendingReview ? formSchemaWithoutBPO : formSchemaWithBPO;

  type FormValues = z.infer<typeof formSchemaWithBPO> | z.infer<typeof formSchemaWithoutBPO>;

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema) as any,
    defaultValues: {
      name: suggestion.content.name as string || "",
      description: suggestion.content.description as string || "",
      rationale: suggestion.rationale || "",
      ...(!isPendingReview && { bpoId: suggestion.assigned_bpo?.id || "" }),
    },
  });

  useEffect(() => {
    async function fetchBPOs() {
      try {
        const supabase = createClient();
        const { data: { session } } = await supabase.auth.getSession();

        if (!session) {
          console.error("No session found - user not logged in");
          return;
        }

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const url = `${apiUrl}/api/v1/users`;

        console.log("Fetching users with auth token from:", url);

        // Call API directly with auth header
        const response = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
          },
        });

        console.log("API Response status:", response.status);

        if (!response.ok) {
          if (response.status === 403) {
            console.error("403 Forbidden: Current user does not have admin role");
            console.error("Current user email:", session.user?.email);
          }
          const errorText = await response.text();
          console.error("API Error:", errorText);
          return;
        }

        const data = await response.json();
        console.log("All users:", data);

        // Handle both paginated and non-paginated responses
        const users = Array.isArray(data) ? data : (data.items || data.data || []);

        const bpoUsers = users.filter((user: any) =>
          user.roles?.includes("bpo")
        );
        console.log("Filtered BPO users:", bpoUsers);
        setBpos(bpoUsers as User[]);

      } catch (error) {
        console.error("Failed to load BPOs:", error);
      }
    }
    if (isOpen) {
      fetchBPOs();
    }
  }, [isOpen]);

  const onSubmitAccept = async (values: z.infer<typeof formSchemaWithBPO>) => {
    // Validate BPO is selected before accepting
    if (!values.bpoId) {
      form.setError("bpoId" as any, {
        type: "manual",
        message: "BPO assignment is required for acceptance",
      });
      return;
    }

    setIsSubmitting(true);
    try {
      const supabase = createClient();
      const { data: { session } } = await supabase.auth.getSession();

      if (!session) {
        console.error("No session found - user not logged in");
        alert("Session expired. Please refresh the page and try again.");
        return;
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const url = `${apiUrl}/api/v1/suggestions/${suggestion.id}/status`;

      console.log("Accepting suggestion:", { url, bpoId: values.bpoId });

      const response = await fetch(url, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          status: "pending_review",
          updated_content: {
            name: values.name,
            description: values.description,
          },
          bpo_id: values.bpoId,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("API Error:", errorText);
        alert(`Failed to accept suggestion: ${response.status} - ${errorText}`);
        throw new Error(`Failed to accept suggestion: ${response.status}`);
      }

      console.log("✅ Suggestion accepted and routed to BPO:", values.bpoId);
      onSuccess();
      onOpenChange(false);
    } catch (error) {
      console.error("Failed to accept suggestion:", error);
      if (error instanceof Error && error.message.includes("fetch")) {
        alert("Network error: Cannot connect to API. Is the backend running?");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const onSubmitReject = async () => {
    setIsSubmitting(true);
    try {
      const supabase = createClient();
      const { data: { session } } = await supabase.auth.getSession();

      if (!session) {
        console.error("No session found - user not logged in");
        alert("Session expired. Please refresh the page and try again.");
        return;
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const url = `${apiUrl}/api/v1/suggestions/${suggestion.id}/status`;

      console.log("Rejecting suggestion:", url);

      const response = await fetch(url, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          status: isPendingReview ? "archived" : "rejected",
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("API Error:", errorText);
        alert(`Failed to reject suggestion: ${response.status} - ${errorText}`);
        throw new Error(`Failed to reject suggestion: ${response.status}`);
      }

      console.log("✅ Suggestion rejected");
      onSuccess();
      onOpenChange(false);
    } catch (error) {
      console.error("Failed to reject suggestion:", error);
      if (error instanceof Error && error.message.includes("fetch")) {
        alert("Network error: Cannot connect to API. Is the backend running?");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const onSubmitApprove = async (values: z.infer<typeof formSchemaWithoutBPO>) => {
    setIsSubmitting(true);
    try {
      const supabase = createClient();
      const { data: { session } } = await supabase.auth.getSession();

      if (!session) {
        console.error("No session found - user not logged in");
        alert("Session expired. Please refresh the page and try again.");
        return;
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const url = `${apiUrl}/api/v1/suggestions/${suggestion.id}/approve`;

      console.log("Approving suggestion:", { url, values });

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          name: values.name,
          description: values.description,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("API Error:", errorText);
        alert(`Failed to approve suggestion: ${response.status} - ${errorText}`);
        throw new Error(`Failed to approve suggestion: ${response.status}`);
      }

      console.log("✅ Suggestion approved and entity created");
      onSuccess();
      onOpenChange(false);
    } catch (error) {
      console.error("Failed to approve suggestion:", error);
      if (error instanceof Error && error.message.includes("fetch")) {
        alert("Network error: Cannot connect to API. Is the backend running?");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const getTypeBadge = (type: string) => {
    switch (type) {
      case "risk":
        return (
          <Badge variant="destructive" className="ml-2 gap-1">
            <AlertCircle className="h-3 w-3" /> Risk
          </Badge>
        );
      case "control":
        return (
          <Badge variant="default" className="ml-2 gap-1">
            <Shield className="h-3 w-3" /> Control
          </Badge>
        );
      case "business_process":
        return (
          <Badge variant="outline" className="ml-2 gap-1 border-purple-500 text-purple-600">
            <Briefcase className="h-3 w-3" /> Process
          </Badge>
        );
      default:
        return <Badge variant="secondary" className="ml-2">{type}</Badge>;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px]">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            {isPendingReview ? "Approve AI Suggestion" : "Review AI Suggestion"}
            {getTypeBadge(suggestion.type)}
          </DialogTitle>
          <DialogDescription>
            {isPendingReview
              ? "Review the suggestion and approve to create the entity, or reject to discard it."
              : "Review and optionally edit the AI-generated suggestion before accepting or rejecting it. Accepting routes the suggestion to a BPO for final approval."}
          </DialogDescription>
        </DialogHeader>
        {/* ... form ... */}
        <Form {...form}>
          <form className="grid gap-4 py-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Suggested Name</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Suggested Description</FormLabel>
                  <FormControl>
                    <Textarea {...field} className="min-h-[100px]" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
             <FormField
              control={form.control}
              name="rationale"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>AI Rationale</FormLabel>
                  <FormControl>
                    <Textarea {...field} className="min-h-[80px]" disabled={isPendingReview} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            {!isPendingReview && (
              <FormField
                control={form.control}
                name={"bpoId" as any}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Assign BPO (Required for Acceptance)</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                      disabled={isSubmitting}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select a BPO to assign" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {bpos.length === 0 ? (
                          <div className="px-2 py-6 text-center text-sm text-muted-foreground">
                            No BPO users found. Create a user with BPO role first.
                          </div>
                        ) : (
                          bpos.map((bpo) => (
                            <SelectItem key={bpo.id} value={bpo.id as string}>
                              {bpo.full_name || bpo.email}
                            </SelectItem>
                          ))
                        )}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}
            {isPendingReview && suggestion.assigned_bpo && (
              <div className="rounded-lg border p-3 bg-muted/50">
                <p className="text-sm font-medium">Assigned BPO</p>
                <p className="text-sm text-muted-foreground mt-1">
                  {suggestion.assigned_bpo.full_name || suggestion.assigned_bpo.email}
                </p>
              </div>
            )}
          </form>
        </Form>
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            onClick={isPendingReview ? onSubmitReject : form.handleSubmit(onSubmitReject)}
            disabled={isSubmitting}
            variant="destructive"
          >
            {isSubmitting ? "Rejecting..." : "Reject"}
          </Button>
          {isPendingReview ? (
            <Button
              type="submit"
              onClick={form.handleSubmit(onSubmitApprove)}
              disabled={isSubmitting}
            >
              {isSubmitting ? "Approving..." : "Approve & Create Entity"}
            </Button>
          ) : (
            <Button
              type="submit"
              onClick={form.handleSubmit(onSubmitAccept)}
              disabled={isSubmitting}
            >
              {isSubmitting ? "Accepting..." : "Accept & Route to BPO"}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
