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
import { readRisks, RiskRead } from "@/app/clientService";
import Link from "next/link";
import { removeRisk } from "@/components/actions/delete-actions";
import { DeleteEntityButton } from "@/components/delete-entity-button";

export default function RisksPage() {
  const [risks, setRisks] = useState<RiskRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRisks = async () => {
    try {
      setLoading(true);
      const response = await readRisks();
      if (response.data && response.data.items) {
        setRisks(response.data.items);
      }
    } catch (err) {
      console.error("Failed to fetch risks:", err);
      setError("Failed to load risks. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRisks();
  }, []);

  const handleDelete = async (id: string) => {
    try {
      await removeRisk(id);
      fetchRisks();
    } catch (error) {
      console.error("Failed to delete risk:", error);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold tracking-tight">Risks</h1>
        <Button asChild>
          <Link href="/dashboard/risks/new">
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
              <TableHead>Category</TableHead>
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
            ) : risks.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={4}
                  className="text-center py-10 text-muted-foreground"
                >
                  No risks found. Create one to get started.
                </TableCell>
              </TableRow>
            ) : (
              risks.map((risk) => (
                <TableRow key={risk.id}>
                  <TableCell className="font-medium">{risk.name}</TableCell>
                  <TableCell>{risk.description}</TableCell>
                  <TableCell>{risk.category}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="icon" asChild>
                        <Link href={`/dashboard/risks/${risk.id}/edit`}>
                          <Pencil className="h-4 w-4" />
                        </Link>
                      </Button>
                      <DeleteEntityButton
                        id={risk.id}
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
