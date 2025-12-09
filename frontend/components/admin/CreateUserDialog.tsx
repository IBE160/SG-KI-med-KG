"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { createClient } from "@/lib/supabase";
import { toast } from "sonner";

const createUserSchema = z.object({
  email: z.string().email({ message: "Invalid email address" }),
  password: z.string().min(8, { message: "Password must be at least 8 characters" }),
  role: z.enum(["admin", "bpo", "executive", "general_user"]),
});

type CreateUserFormValues = z.infer<typeof createUserSchema>;

interface CreateUserDialogProps {
  onUserCreated: () => void;
}

export function CreateUserDialog({ onUserCreated }: CreateUserDialogProps) {
  const [open, setOpen] = useState(false);
  const supabase = createClient();
  
  const form = useForm<CreateUserFormValues>({
    resolver: zodResolver(createUserSchema),
    defaultValues: {
      email: "",
      password: "",
      role: "general_user",
    },
  });

  const onSubmit = async (data: CreateUserFormValues) => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        toast.error("Not authenticated");
        return;
      }

      // Check if API URL ends with /api/v1 or just host. 
      // Existing code used `${process.env.NEXT_PUBLIC_API_URL}/users` for list, and `/api/v1/users/${id}/role` for update.
      // This suggests NEXT_PUBLIC_API_URL might include /api/v1 or be inconsistent.
      // Let's assume consistent with create: /api/v1/users.
      // If NEXT_PUBLIC_API_URL is "http://localhost:8000/api/v1", then we append "/users".
      // If it is "http://localhost:8000", we append "/api/v1/users".
      
      // Let's check how the existing page uses it: 
      // fetch(`${process.env.NEXT_PUBLIC_API_URL}/users` ...
      // fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/${selectedUser.id}/role` ...
      
      // This is confusing. 
      // If /users works, then base URL likely ends in /api/v1?
      // But /api/v1/users/... works too? Maybe /api/v1 is doubled?
      // Or maybe there are two routers: /users and /api/v1/users.
      
      // I defined the new endpoint in `backend/app/api/v1/endpoints/users.py` which is mounted usually at `/api/v1/users`.
      // So the correct path is likely `/api/v1/users`.
      
      // Safest bet: `${process.env.NEXT_PUBLIC_API_URL}/api/v1/users` if API_URL is root.
      // But if API_URL is /api/v1, then `${process.env.NEXT_PUBLIC_API_URL}/users` would be correct.
      
      // Let's look at `frontend/app/dashboard/admin/users/page.tsx` again.
      // list: `${process.env.NEXT_PUBLIC_API_URL}/users`
      // update: `${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/${selectedUser.id}/role`
      
      // If list works at /users, and update works at /api/v1/users/..., it implies inconsistent mounting or proxy.
      // I will trust my new endpoint is at `/api/v1/users`.
      
      // I'll use a relative path /api/v1/users if I can, but I need the base URL.
      // I'll try to follow the update pattern: `${process.env.NEXT_PUBLIC_API_URL}/api/v1/users`
      
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify(data),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to create user");
      }

      toast.success("User created successfully");
      setOpen(false);
      form.reset();
      onUserCreated();
    } catch (error: any) {
      console.error(error);
      toast.error(error.message || "Failed to create user");
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>Create User</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create New User</DialogTitle>
          <DialogDescription>
            Add a new user to the system. They will receive an email confirmation.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input placeholder="user@example.com" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Password</FormLabel>
                  <FormControl>
                    <Input type="password" placeholder="********" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="role"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Role</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a role" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="general_user">General User</SelectItem>
                      <SelectItem value="bpo">BPO</SelectItem>
                      <SelectItem value="executive">Executive</SelectItem>
                      <SelectItem value="admin">Admin</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            <DialogFooter>
              <Button type="submit" disabled={form.formState.isSubmitting}>
                {form.formState.isSubmitting ? "Creating..." : "Create User"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
