"use client";

import * as React from "react";
import {
  useControls,
  useRegulatoryFrameworks,
  useControlMappings,
  useRequirementMappings,
  useCreateMapping,
  useDeleteMapping,
} from "@/hooks/useMappings";
import { DualListSelector, DualListItem } from "@/components/custom/DualListSelector";
import { RoleGuard } from "@/lib/role";
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
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { ExclamationTriangleIcon } from "@radix-ui/react-icons";

type ViewMode = "control" | "requirement";

export default function ComplianceMappingPage() {
  const [viewMode, setViewMode] = React.useState<ViewMode>("control");
  const [selectedId, setSelectedId] = React.useState<string>("");

  // Data Hooks
  const {
    data: controlsData,
    isLoading: controlsLoading,
    error: controlsError,
  } = useControls();

  const {
    data: requirementsData,
    isLoading: requirementsLoading,
    error: requirementsError,
  } = useRegulatoryFrameworks();

  // Mapping Hooks - Conditional fetching
  const {
    data: controlMappingsData,
    isLoading: controlMappingsLoading,
  } = useControlMappings(viewMode === "control" ? selectedId : null);

  const {
    data: requirementMappingsData,
    isLoading: requirementMappingsLoading,
  } = useRequirementMappings(viewMode === "requirement" ? selectedId : null);

  // Mutation Hooks
  const createMutation = useCreateMapping();
  const deleteMutation = useDeleteMapping();

  // Reset selection when switching views
  const handleViewChange = (mode: string) => {
    setViewMode(mode as ViewMode);
    setSelectedId("");
  };

  // Prepare data for DualListSelector
  const { availableItems, selectedItems } = React.useMemo(() => {
    if (!selectedId) return { availableItems: [], selectedItems: [] };

    let allItems: DualListItem[] = [];
    let mappedIds: string[] = [];

    if (viewMode === "control") {
      // Mapping Requirements to a Control
      allItems = requirementsData?.items?.map((r: { id: string; name: string }) => ({ id: r.id, name: r.name })) || [];
      mappedIds = controlMappingsData?.mappings?.map((m: { regulatory_requirement_id: string }) => m.regulatory_requirement_id) || [];
    } else {
      // Mapping Controls to a Requirement
      allItems = controlsData?.items?.map((c: { id: string; name: string }) => ({ id: c.id, name: c.name })) || [];
      mappedIds = requirementMappingsData?.mappings?.map((m: { control_id: string }) => m.control_id) || [];
    }

    const selected = allItems.filter((item) => mappedIds.includes(item.id));
    const available = allItems.filter((item) => !mappedIds.includes(item.id));

    return { availableItems: available, selectedItems: selected };
  }, [
    viewMode,
    selectedId,
    controlsData,
    requirementsData,
    controlMappingsData,
    requirementMappingsData,
  ]);

  // Handle Selection Change (Add/Remove)
  const handleSelectionChange = async (newSelectedIds: string[]) => {
    if (!selectedId) return;

    const currentSelectedIds = selectedItems.map((i) => i.id);
    
    // Find additions
    const addedIds = newSelectedIds.filter((id) => !currentSelectedIds.includes(id));
    // Find removals
    const removedIds = currentSelectedIds.filter((id) => !newSelectedIds.includes(id));

    // Determine IDs based on view mode
    const executeMutation = async (
      action: "create" | "delete",
      itemId: string
    ) => {
      const controlId = viewMode === "control" ? selectedId : itemId;
      const requirementId = viewMode === "control" ? itemId : selectedId;

      if (action === "create") {
        await createMutation.mutateAsync({ controlId, requirementId });
      } else {
        await deleteMutation.mutateAsync({ controlId, requirementId });
      }
    };

    // Execute additions
    for (const id of addedIds) {
      await executeMutation("create", id);
    }

    // Execute removals
    for (const id of removedIds) {
      await executeMutation("delete", id);
    }
  };

  const isLoading =
    controlsLoading ||
    requirementsLoading ||
    (selectedId && (controlMappingsLoading || requirementMappingsLoading));

  if (controlsError || requirementsError) {
    return (
      <RoleGuard allowedRoles={["admin"]}>
        <div className="p-8">
          <Alert variant="destructive">
            <ExclamationTriangleIcon className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>
              Failed to load data. Please try again later.
            </AlertDescription>
          </Alert>
        </div>
      </RoleGuard>
    );
  }

  return (
    <RoleGuard allowedRoles={["admin"]}>
      <div className="p-8 max-w-7xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">Compliance Mapping</h1>
          <p className="text-muted-foreground">
            Map internal controls to regulatory framework requirements
          </p>
        </div>

        {/* View Perspective Toggle */}
        <Tabs value={viewMode} onValueChange={handleViewChange}>
          <TabsList>
            <TabsTrigger value="control">Control Perspective</TabsTrigger>
            <TabsTrigger value="requirement">Requirement Perspective</TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Item Selector */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">
              Select {viewMode === "control" ? "Control" : "Requirement"}
            </CardTitle>
            <CardDescription>
              Choose a {viewMode} to manage its mappings
            </CardDescription>
          </CardHeader>
          <CardContent>
            {controlsLoading || requirementsLoading ? (
              <Skeleton className="h-10 w-full" />
            ) : (
              <Select value={selectedId} onValueChange={setSelectedId}>
                <SelectTrigger className="w-full">
                  <SelectValue
                    placeholder={`Select a ${viewMode}...`}
                  />
                </SelectTrigger>
                <SelectContent>
                  {viewMode === "control"
                    ? controlsData?.items?.map((control: { id: string; name: string }) => (
                        <SelectItem key={control.id} value={control.id}>
                          {control.name}
                        </SelectItem>
                      ))
                    : requirementsData?.items?.map((req: { id: string; name: string }) => (
                        <SelectItem key={req.id} value={req.id}>
                          {req.name}
                        </SelectItem>
                      ))}
                </SelectContent>
              </Select>
            )}
          </CardContent>
        </Card>

        {/* Mapping Interface */}
        {selectedId ? (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Manage Mappings</CardTitle>
              <CardDescription>
                Associate {viewMode === "control" ? "requirements" : "controls"} with the selected {viewMode}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-4">
                  <Skeleton className="h-[400px] w-full" />
                </div>
              ) : (
                <DualListSelector
                  availableItems={availableItems}
                  selectedItems={selectedItems}
                  onSelectionChange={handleSelectionChange}
                  availableTitle={`Available ${
                    viewMode === "control" ? "Requirements" : "Controls"
                  }`}
                  selectedTitle={`Mapped ${
                    viewMode === "control" ? "Requirements" : "Controls"
                  }`}
                />
              )}
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="py-12">
              <div className="text-center text-muted-foreground">
                <p className="text-lg mb-2">Select an item to get started</p>
                <p className="text-sm">
                  Choose a {viewMode} from the dropdown above to manage its mappings
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </RoleGuard>
  );
}