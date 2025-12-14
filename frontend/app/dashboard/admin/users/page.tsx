"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase";
import { UserRead } from "@/app/clientService";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { ExclamationTriangleIcon } from "@radix-ui/react-icons";
import { RoleGuard } from "@/lib/role";
import { CreateUserDialog } from "@/components/admin/CreateUserDialog";

export default function UsersPage() {
  const [users, setUsers] = useState<UserRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedUser, setSelectedUser] = useState<UserRead | null>(null);
  const [newRoles, setNewRoles] = useState<string[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const supabase = createClient();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (!session) {
        throw new Error("Not authenticated");
      }

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users`, {
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!res.ok) {
        if (res.status === 403) {
          throw new Error("Access denied: Admin privileges required.");
        }
        throw new Error("Failed to fetch users");
      }

      const data = await res.json();
      setUsers(data.items || data); // Handle pagination if present
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateRoles = async () => {
    if (!selectedUser || newRoles.length === 0) return;

    // Validate role combination (AC 1)
    if (newRoles.includes("general_user") && newRoles.length > 1) {
      setValidationError("general_user cannot be combined with other roles");
      return;
    }

    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (!session) return;

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/${selectedUser.id}/roles`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${session.access_token}`,
          },
          body: JSON.stringify({ roles: newRoles }),
        },
      );

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to update roles");
      }

      // Update local state
      setUsers(
        users.map((u) =>
          u.id === selectedUser.id ? { ...u, roles: newRoles } : u,
        ),
      );
      setDialogOpen(false);
      setSelectedUser(null);
      setNewRoles([]);
      setValidationError(null);
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) return <div className="p-8">Loading users...</div>;
  if (error)
    return (
      <div className="p-8">
        <Alert variant="destructive">
          <ExclamationTriangleIcon className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );

  return (
    <RoleGuard allowedRoles={["admin"]}>
      <div className="container mx-auto py-10">
        <div className="flex justify-between items-center mb-5">
          <h1 className="text-2xl font-bold">User Management</h1>
          <CreateUserDialog onUserCreated={fetchUsers} />
        </div>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Active</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell
                    className="font-medium truncate max-w-[100px]"
                    title={user.id}
                  >
                    {user.id}
                  </TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    <div className="flex gap-1 flex-wrap">
                      {user.roles && user.roles.length > 0 ? (
                        user.roles.map((role) => (
                          <Badge
                            key={role}
                            variant={
                              role === "admin" ? "default" :
                              role === "bpo" ? "secondary" :
                              role === "executive" ? "outline" :
                              "destructive"
                            }
                            className="capitalize"
                          >
                            {role === "general_user" ? "General" : role}
                          </Badge>
                        ))
                      ) : (
                        <Badge variant="destructive" className="capitalize">
                          unknown
                        </Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>{user.is_active ? "Yes" : "No"}</TableCell>
                  <TableCell className="text-right">
                    <Dialog
                      open={dialogOpen && selectedUser?.id === user.id}
                      onOpenChange={(open) => {
                        if (open) {
                          setSelectedUser(user);
                          setNewRoles(user.roles || ["general_user"]);
                          setValidationError(null);
                        } else {
                          setSelectedUser(null);
                          setValidationError(null);
                        }
                        setDialogOpen(open);
                      }}
                    >
                      <DialogTrigger asChild>
                        <Button variant="outline" size="sm">
                          Edit Role
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Edit Roles for {user.email}</DialogTitle>
                          <DialogDescription>
                            Select one or more roles for this user. Note: general_user cannot be combined with other roles.
                          </DialogDescription>
                        </DialogHeader>
                        <div className="grid gap-4 py-4">
                          {validationError && (
                            <Alert variant="destructive">
                              <ExclamationTriangleIcon className="h-4 w-4" />
                              <AlertDescription>{validationError}</AlertDescription>
                            </Alert>
                          )}
                          <div className="space-y-3">
                            {[
                              { value: "general_user", label: "General User" },
                              { value: "bpo", label: "Business Process Owner" },
                              { value: "executive", label: "Executive" },
                              { value: "admin", label: "Admin" },
                            ].map((role) => {
                              const isGeneralUser = role.value === "general_user";
                              const hasGeneralUser = newRoles.includes("general_user");
                              const hasOtherRoles = newRoles.some(r => r !== "general_user");

                              // Disable general_user if other roles selected
                              // Disable other roles if general_user selected
                              const isDisabled = isGeneralUser
                                ? hasOtherRoles
                                : hasGeneralUser;

                              return (
                                <label
                                  key={role.value}
                                  className={`flex items-center space-x-2 cursor-pointer ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                                >
                                  <input
                                    type="checkbox"
                                    checked={newRoles.includes(role.value)}
                                    disabled={isDisabled}
                                    onChange={(e) => {
                                      if (e.target.checked) {
                                        setNewRoles([...newRoles, role.value]);
                                      } else {
                                        setNewRoles(newRoles.filter(r => r !== role.value));
                                      }
                                      setValidationError(null);
                                    }}
                                    className="w-4 h-4 rounded border-gray-300"
                                  />
                                  <span className="text-sm">{role.label}</span>
                                </label>
                              );
                            })}
                          </div>
                        </div>
                        <DialogFooter>
                          <Button
                            variant="outline"
                            onClick={() => setDialogOpen(false)}
                          >
                            Cancel
                          </Button>
                          <Button onClick={handleUpdateRoles}>
                            Save Changes
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>
    </RoleGuard>
  );
}
