"use client";

import { useEffect, useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Plus, Pencil } from "lucide-react";
import {
  readRegulatoryFrameworks,
  RegulatoryFrameworkRead,
} from "@/app/clientService";
import Link from "next/link";
import { removeRegulatoryFramework } from "@/components/actions/delete-actions";
import { DeleteEntityButton } from "@/components/delete-entity-button";

export default function RegulatoryFrameworksPage() {
  const [frameworks, setFrameworks] = useState<RegulatoryFrameworkRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFrameworks = async () => {
    try {
      setLoading(true);
      const response = await readRegulatoryFrameworks();
      if (response.data && response.data.items) {
        setFrameworks(response.data.items);
      }
    } catch (err) {
      console.error("Failed to fetch regulatory frameworks:", err);
      setError("Failed to load regulatory frameworks. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFrameworks();
  }, []);

  const handleDelete = async (id: string) => {
    try {
      await removeRegulatoryFramework(id);
      fetchFrameworks();
    } catch (error) {
      console.error("Failed to delete regulatory framework:", error);
    }
  };

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

      <div className="border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Version</TableHead>
              <TableHead className="w-[100px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-10">
                  Loading...
                </TableCell>
              </TableRow>
            ) : error ? (
              <TableRow>
                <TableCell
                  colSpan={4}
                  className="text-center py-10 text-red-500"
                >
                  {error}
                </TableCell>
              </TableRow>
            ) : frameworks.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={4}
                  className="text-center py-10 text-muted-foreground"
                >
                  No regulatory frameworks found. Create one to get started.
                </TableCell>
              </TableRow>
            ) : (
              frameworks.map((framework) => (
                <TableRow key={framework.id}>
                  <TableCell className="font-medium">
                    {framework.name}
                  </TableCell>
                  <TableCell>{framework.description}</TableCell>
                  <TableCell>{framework.version}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="icon" asChild>
                        <Link
                          href={`/dashboard/regulatory-frameworks/${framework.id}/edit`}
                        >
                          <Pencil className="h-4 w-4" />
                        </Link>
                      </Button>
                      <DeleteEntityButton
                        id={framework.id}
                        onDelete={handleDelete}
                      />
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
