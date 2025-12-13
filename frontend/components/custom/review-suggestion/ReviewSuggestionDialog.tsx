"use client";

import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { v4 as uuidv4 } from "uuid"; // For generating temporary unique keys if needed
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
import { AISuggestionRead, SuggestionStatus } from "@/app/openapi-client/types.gen";
import { listUsers, updateSuggestionStatus } from "@/app/clientService";
import { useRole } from "@/lib/role"; // Assuming useRole provides current user's role and tenant info
import { useToast } from "@/components/ui/use-toast";
import { UUID } from "crypto";

interface User {
  id: UUID;
  full_name: string;
  email: string;
  role: string;
}

const formSchema = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().optional(),
  rationale: z.string().optional(),
  bpoId: z.string().uuid().optional(), // BPO ID is optional for some actions
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
  // ... existing code

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
            Review AI Suggestion
            {getTypeBadge(suggestion.type)}
          </DialogTitle>
          <DialogDescription>
            Review and optionally edit the AI-generated suggestion before accepting or rejecting it.
            Accepting routes the suggestion to a BPO for final approval.
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
                    <Textarea {...field} className="min-h-[80px]" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="bpoId"
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
                      {bpos.map((bpo) => (
                        <SelectItem key={bpo.id} value={bpo.id as string}>
                          {bpo.full_name || bpo.email}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
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
            onClick={form.handleSubmit(onSubmitReject)}
            disabled={isSubmitting}
            variant="destructive"
          >
            {isSubmitting ? "Rejecting..." : "Reject"}
          </Button>
          <Button
            type="submit"
            onClick={form.handleSubmit(onSubmitAccept)}
            disabled={isSubmitting}
          >
            {isSubmitting ? "Accepting..." : "Accept & Route to BPO"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
