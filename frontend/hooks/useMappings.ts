import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  client,
  readControls,
  readRegulatoryFrameworks,
  createMapping,
  deleteMapping,
  getMappingsForControl,
  getMappingsForRequirement,
} from "@/app/clientService";

// Cache keys
export const MAPPING_KEYS = {
  all: ["mappings"] as const,
  controls: ["controls"] as const,
  frameworks: ["regulatory-frameworks"] as const,
  controlMappings: (controlId: string) => [...MAPPING_KEYS.all, "control", controlId] as const,
  requirementMappings: (requirementId: string) => [...MAPPING_KEYS.all, "requirement", requirementId] as const,
};

export function useControls() {
  return useQuery({
    queryKey: MAPPING_KEYS.controls,
    queryFn: async () => {
      const response = await readControls({ client });
      return response.data;
    },
  });
}

export function useRegulatoryFrameworks() {
  return useQuery({
    queryKey: MAPPING_KEYS.frameworks,
    queryFn: async () => {
      const response = await readRegulatoryFrameworks({ client });
      return response.data;
    },
  });
}

export function useControlMappings(controlId: string | null) {
  return useQuery({
    queryKey: MAPPING_KEYS.controlMappings(controlId || ""),
    queryFn: async () => {
      if (!controlId) return null;
      const response = await getMappingsForControl({
        client,
        path: { control_id: controlId },
      });
      return response.data;
    },
    enabled: !!controlId,
    staleTime: 60 * 1000, // 60s cache TTL
  });
}

export function useRequirementMappings(requirementId: string | null) {
  return useQuery({
    queryKey: MAPPING_KEYS.requirementMappings(requirementId || ""),
    queryFn: async () => {
      if (!requirementId) return null;
      const response = await getMappingsForRequirement({
        client,
        path: { requirement_id: requirementId },
      });
      return response.data;
    },
    enabled: !!requirementId,
    staleTime: 60 * 1000, // 60s cache TTL
  });
}

export function useCreateMapping() {
  const queryClient = useQueryClient();

  return useMutation({
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
    onSuccess: (data, variables) => {
      // Invalidate both control and requirement mapping queries
      queryClient.invalidateQueries({
        queryKey: MAPPING_KEYS.controlMappings(variables.controlId),
      });
      queryClient.invalidateQueries({
        queryKey: MAPPING_KEYS.requirementMappings(variables.requirementId),
      });
      toast.success("Mapping created successfully");
    },
    onError: (error: any) => {
      const errorMessage =
        error?.response?.data?.detail || "Failed to create mapping";
      toast.error(errorMessage);
    },
  });
}

export function useDeleteMapping() {
  const queryClient = useQueryClient();

  return useMutation({
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
    onSuccess: (data, variables) => {
      // Invalidate both control and requirement mapping queries
      queryClient.invalidateQueries({
        queryKey: MAPPING_KEYS.controlMappings(variables.controlId),
      });
      queryClient.invalidateQueries({
        queryKey: MAPPING_KEYS.requirementMappings(variables.requirementId),
      });
      toast.success("Mapping removed successfully");
    },
    onError: (error: any) => {
      const errorMessage =
        error?.response?.data?.detail || "Failed to remove mapping";
      toast.error(errorMessage);
    },
  });
}
