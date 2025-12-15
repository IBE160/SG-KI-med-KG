"use client";

import { useEffect, useState } from "react";
import { Plus, Pencil, ScrollText, ClipboardList, FileText, ChevronRight, ChevronDown } from "lucide-react";
import {
  getRegulatoryFrameworksTree,
  RegulatoryFrameworkTreeItem,
  deleteRegulatoryFramework,
} from "@/app/clientService";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { DeleteEntityButton } from "@/components/delete-entity-button";
import { TreeItem } from "@/components/custom/TreeItem"; // Import the TreeItem component
import { Badge } from "@/components/ui/badge";

export default function RegulatoryFrameworksPage() {
  const [frameworksTree, setFrameworksTree] = useState<RegulatoryFrameworkTreeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFrameworksTree = async () => {
    try {
      setLoading(true);
      const response = await getRegulatoryFrameworksTree();
      if (response.data) {
        setFrameworksTree(response.data);
      }
    } catch (err) {
      console.error("Failed to fetch regulatory frameworks tree:", err);
      setError("Failed to load regulatory frameworks. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFrameworksTree();
  }, []);

  const handleDelete = async (id: string, isRequirement: boolean) => {
    try {
      // Assuming deleteRegulatoryFramework can handle both frameworks and requirements
      // Or we need a separate function for requirements (not in current API)
      await deleteRegulatoryFramework({ path: { framework_id: id } }); // This needs to be updated if requirements have separate delete API
      fetchFrameworksTree();
    } catch (error) {
      console.error("Failed to delete regulatory item:", error);
    }
  };

  const ActionButtons = ({ item, isRequirement = false }: { item: any, isRequirement?: boolean }) => (
    <div className="flex items-center gap-1">
      <Button variant="ghost" size="icon" asChild>
        <Link href={`/dashboard/regulatory-frameworks/${item.id}/edit`}>
          <Pencil className="h-4 w-4" />
        </Link>
      </Button>
      <DeleteEntityButton
        id={item.id}
        onDelete={() => handleDelete(item.id, isRequirement)}
      />
    </div>
  );

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold tracking-tight">
          Regulatory Frameworks
        </h1>
        <Button asChild>
          <Link href="/dashboard/regulatory-frameworks/new">
            <Plus className="mr-2 h-4 w-4" />
            Create New
          </Link>
        </Button>
      </div>

      <div className="border rounded-md p-4">
        {loading ? (
          <div className="space-y-2">
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
          </div>
        ) : error ? (
          <div className="text-center py-10 text-red-500">{error}</div>
        ) : frameworksTree.length === 0 ? (
          <div className="text-center py-10 text-muted-foreground">
            No regulatory frameworks found. Create one to get started.
          </div>
        ) : (
          <div className="space-y-2">
            {frameworksTree.map((framework) => (
              <TreeItem
                key={framework.id}
                label={framework.name}
                icon={ScrollText} // Icon for Main Law
                badgeCount={framework.requirements?.length ?? 0}
                actions={<ActionButtons item={framework} />}
                defaultExpanded={true}
              >
                {framework.description && (
                  <div className="text-sm text-muted-foreground ml-2">
                    {framework.description} (v{framework.version || 'N/A'})
                    {framework.document_id && (
                      <span className="ml-2 text-xs flex items-center gap-1">
                        <FileText className="h-3 w-3" /> Linked Document
                      </span>
                    )}
                  </div>
                )}
                {framework.requirements?.map((requirement) => (
                  <TreeItem
                    key={requirement.id}
                    label={requirement.name}
                    icon={ClipboardList} // Icon for Regulation
                    actions={<ActionButtons item={requirement} isRequirement={true} />}
                  >
                    {requirement.description && (
                      <div className="text-sm text-muted-foreground ml-2">
                        {requirement.description}
                        {requirement.document_id && (
                          <span className="ml-2 text-xs flex items-center gap-1">
                            <FileText className="h-3 w-3" /> Linked Document
                          </span>
                        )}
                      </div>
                    )}
                  </TreeItem>
                ))}
              </TreeItem>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
