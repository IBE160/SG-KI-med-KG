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
  readBusinessProcesses,
  BusinessProcessRead,
} from "@/app/clientService";
import Link from "next/link";
import { removeBusinessProcess } from "@/components/actions/delete-actions";
import { DeleteEntityButton } from "@/components/delete-entity-button";

export default function BusinessProcessesPage() {
  const [processes, setProcesses] = useState<BusinessProcessRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProcesses = async () => {
    try {
      setLoading(true);
      const response = await readBusinessProcesses();
      if (response.data && response.data.items) {
        setProcesses(response.data.items);
      }
    } catch (err) {
      console.error("Failed to fetch business processes:", err);
      setError("Failed to load business processes. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProcesses();
  }, []);

  const handleDelete = async (id: string) => {
    try {
      await removeBusinessProcess(id);
      fetchProcesses();
    } catch (error) {
      console.error("Failed to delete business process:", error);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold tracking-tight">
          Business Processes
        </h1>
        <Button asChild>
          <Link href="/dashboard/business-processes/new">
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
              <TableHead className="w-[100px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={3} className="text-center py-10">
                  Loading...
                </TableCell>
              </TableRow>
            ) : error ? (
              <TableRow>
                <TableCell
                  colSpan={3}
                  className="text-center py-10 text-red-500"
                >
                  {error}
                </TableCell>
              </TableRow>
            ) : processes.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={3}
                  className="text-center py-10 text-muted-foreground"
                >
                  No business processes found. Create one to get started.
                </TableCell>
              </TableRow>
            ) : (
              processes.map((process) => (
                <TableRow key={process.id}>
                  <TableCell className="font-medium">{process.name}</TableCell>
                  <TableCell>{process.description}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="icon" asChild>
                        <Link
                          href={`/dashboard/business-processes/${process.id}/edit`}
                        >
                          <Pencil className="h-4 w-4" />
                        </Link>
                      </Button>
                      <DeleteEntityButton
                        id={process.id}
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
