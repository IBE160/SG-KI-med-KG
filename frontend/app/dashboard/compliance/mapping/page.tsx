"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { client } from "@/app/clientService";
import {
  createMapping,
  deleteMapping,
  getMappingsForControl,
  getControls,
  getRegulatoryFrameworks,
} from "@/app/openapi-client";
import { DualListSelector, DualListItem } from "@/components/custom/DualListSelector";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";

export default function ComplianceMappingPage() {
  const [selectedControlId, setSelectedControlId] = React.useState<string>("");
  const queryClient = useQueryClient();

  // Fetch all controls
  const {
    data: controlsData,
    isLoading: controlsLoading,
    error: controlsError,
  } = useQuery({
    queryKey: ["controls"],
    queryFn: async () => {
      const response = await getControls({
        client,
      });
      return response.data;
    },
  });

  // Fetch all regulatory frameworks
  const {
    data: requirementsData,
    isLoading: requirementsLoading,
    error: requirementsError,
  } = useQuery({
    queryKey: ["regulatory-frameworks"],
    queryFn: async () => {
      const response = await getRegulatoryFrameworks({
        client,
      });
      return response.data;
    },
  });

  // Fetch mappings for selected control
  const {
    data: mappingsData,
    isLoading: mappingsLoading,
    refetch: refetchMappings,
  } = useQuery({
    queryKey: ["mappings", selectedControlId],
    queryFn: async () => {
      if (!selectedControlId) return null;
      const response = await getMappingsForControl({
        client,
        path: { control_id: selectedControlId },
      });
      return response.data;
    },
    enabled: !!selectedControlId,
  });

  // Create mapping mutation
  const createMappingMutation = useMutation({
    mutationFn: async ({
      controlId,
      requirementId,
    }: {
      controlId: string;
      requirementId: string;
    }) => {
      const response = await createMapping({
        client,
        body: {
          control_id: controlId,
          regulatory_requirement_id: requirementId,
        },
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mappings", selectedControlId] });
      toast.success("Mapping created successfully");
    },
    onError: (error: any) => {
      const errorMessage =
        error?.response?.data?.detail || "Failed to create mapping";
      toast.error(errorMessage);
    },
  });

  // Delete mapping mutation
  const deleteMappingMutation = useMutation({
    mutationFn: async ({
      controlId,
      requirementId,
    }: {
      controlId: string;
      requirementId: string;
    }) => {
      await deleteMapping({
        client,
        body: {
          control_id: controlId,
          regulatory_requirement_id: requirementId,
        },
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mappings", selectedControlId] });
      toast.success("Mapping removed successfully");
    },
    onError: (error: any) => {
      const errorMessage =
        error?.response?.data?.detail || "Failed to remove mapping";
      toast.error(errorMessage);
    },
  });

  // Convert requirements to DualListItems
  const allRequirements: DualListItem[] = React.useMemo(
    () =>
      requirementsData?.map((req) => ({
        id: req.id,
        name: req.name,
      })) || [],
    [requirementsData]
  );

  // Get currently mapped requirement IDs
  const mappedRequirementIds: string[] = React.useMemo(
    () =>
      mappingsData?.mappings?.map((m) => m.regulatory_requirement_id) || [],
    [mappingsData]
  );

  // Split requirements into available and selected
  const availableRequirements = allRequirements.filter(
    (req) => !mappedRequirementIds.includes(req.id)
  );

  const selectedRequirements = allRequirements.filter((req) =>
    mappedRequirementIds.includes(req.id)
  );

  // Handle selection change
  const handleSelectionChange = async (newSelectedIds: string[]) => {
    if (!selectedControlId) return;

    // Find additions
    const addedIds = newSelectedIds.filter(
      (id) => !mappedRequirementIds.includes(id)
    );

    // Find removals
    const removedIds = mappedRequirementIds.filter(
      (id) => !newSelectedIds.includes(id)
    );

    // Execute additions
    for (const requirementId of addedIds) {
      await createMappingMutation.mutateAsync({
        controlId: selectedControlId,
        requirementId,
      });
    }

    // Execute removals
    for (const requirementId of removedIds) {
      await deleteMappingMutation.mutateAsync({
        controlId: selectedControlId,
        requirementId,
      });
    }
  };

  if (controlsError || requirementsError) {
    return (
      <div className="p-8">
        <Card>
          <CardHeader>
            <CardTitle>Error</CardTitle>
            <CardDescription>
              Failed to load data. Please try again later.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Compliance Mapping</h1>
        <p className="text-muted-foreground">
          Map internal controls to regulatory framework requirements
        </p>
      </div>

      {/* Control Selector */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-lg">Select Control</CardTitle>
          <CardDescription>
            Choose a control to view and manage its regulatory requirement mappings
          </CardDescription>
        </CardHeader>
        <CardContent>
          {controlsLoading ? (
            <Skeleton className="h-10 w-full" />
          ) : (
            <Select
              value={selectedControlId}
              onValueChange={setSelectedControlId}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select a control..." />
              </SelectTrigger>
              <SelectContent>
                {controlsData?.map((control) => (
                  <SelectItem key={control.id} value={control.id}>
                    {control.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </CardContent>
      </Card>

      {/* Mapping Interface */}
      {selectedControlId && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Manage Mappings</CardTitle>
            <CardDescription>
              Add or remove regulatory requirements for the selected control
            </CardDescription>
          </CardHeader>
          <CardContent>
            {requirementsLoading || mappingsLoading ? (
              <div className="space-y-4">
                <Skeleton className="h-[400px] w-full" />
              </div>
            ) : (
              <DualListSelector
                availableItems={availableRequirements}
                selectedItems={selectedRequirements}
                onSelectionChange={handleSelectionChange}
                availableTitle="Available Requirements"
                selectedTitle="Mapped Requirements"
              />
            )}
          </CardContent>
        </Card>
      )}

      {!selectedControlId && (
        <Card>
          <CardContent className="py-12">
            <div className="text-center text-muted-foreground">
              <p className="text-lg mb-2">Select a control to get started</p>
              <p className="text-sm">
                Choose a control from the dropdown above to manage its regulatory
                requirement mappings
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
