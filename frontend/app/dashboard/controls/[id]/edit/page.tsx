"use client";

import { use, useEffect, useState } from "react";
import { useFormState, useFormStatus } from "react-dom";
import { editControl } from "@/components/actions/compliance-actions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { readControl } from "@/app/clientService";
import { toast } from "sonner";

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <Button type="submit" className="w-full" disabled={pending}>
      {pending ? "Updating..." : "Update Control"}
    </Button>
  );
}

export default function EditControlPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [state, action] = useFormState(editControl, undefined);
  const [loading, setLoading] = useState(true);
  const [initialData, setInitialData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await readControl({
          path: { control_id: id },
        });
        if (response.data) {
          setInitialData(response.data);
        }
      } catch (err) {
        console.error("Failed to fetch control:", err);
        setError("Failed to load control data.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  useEffect(() => {
    if (state?.message) {
      toast.error(state.message);
    }
  }, [state]);

  if (loading) {
    return <div className="text-center py-10">Loading...</div>;
  }

  if (error) {
    return <div className="text-center py-10 text-red-500">{error}</div>;
  }

  return (
    <div className="flex justify-center items-center min-h-[calc(100vh-200px)]">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Edit Control</CardTitle>
          <CardDescription>Update the details of this control.</CardDescription>
        </CardHeader>
        <CardContent>
          <form action={action} className="space-y-4">
            <input type="hidden" name="id" value={id} />
            
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                name="name"
                placeholder="Control Name"
                defaultValue={initialData?.name}
              />
              {state?.errors?.name && (
                <p className="text-sm text-red-500">{state.errors.name[0]}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="type">Type</Label>
              <Input
                id="type"
                name="type"
                placeholder="e.g., Preventive"
                defaultValue={initialData?.type || ""}
              />
              {state?.errors?.type && (
                <p className="text-sm text-red-500">{state.errors.type[0]}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                name="description"
                placeholder="Description of the control"
                defaultValue={initialData?.description || ""}
              />
              {state?.errors?.description && (
                <p className="text-sm text-red-500">
                  {state.errors.description[0]}
                </p>
              )}
            </div>

            <SubmitButton />
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
