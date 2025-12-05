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
import { readControls, ControlRead } from "@/app/clientService";
import Link from "next/link";
import { removeControl } from "@/components/actions/delete-actions";
import { DeleteEntityButton } from "@/components/delete-entity-button";

export default function ControlsPage() {
  const [controls, setControls] = useState<ControlRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchControls = async () => {
    try {
      setLoading(true);
      const response = await readControls();
      if (response.data && response.data.items) {
        setControls(response.data.items);
      }
    } catch (err) {
      console.error("Failed to fetch controls:", err);
      setError("Failed to load controls. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchControls();
  }, []);

  const handleDelete = async (id: string) => {
    try {
      await removeControl(id);
      // Refresh the list after deletion
      fetchControls();
    } catch (error) {
      console.error("Failed to delete control:", error);
      // Optionally show an error toast here
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold tracking-tight">Controls</h1>
        <Button asChild>
          <Link href="/dashboard/controls/new">
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
              <TableHead>Type</TableHead>
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
            ) : controls.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={4}
                  className="text-center py-10 text-muted-foreground"
                >
                  No controls found. Create one to get started.
                </TableCell>
              </TableRow>
            ) : (
              controls.map((control) => (
                <TableRow key={control.id}>
                  <TableCell className="font-medium">{control.name}</TableCell>
                  <TableCell>{control.description}</TableCell>
                  <TableCell>{control.type}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="icon" asChild>
                        <Link href={`/dashboard/controls/${control.id}/edit`}>
                          <Pencil className="h-4 w-4" />
                        </Link>
                      </Button>
                      <DeleteEntityButton
                        id={control.id}
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
