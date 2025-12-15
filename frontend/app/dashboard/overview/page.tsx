"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  LayoutDashboard, 
  ChevronRight, 
  ChevronDown, 
  Shield, 
  AlertTriangle, 
  FileText, 
  Settings,
  Edit,
  Trash2
} from "lucide-react";
import { useRole } from "@/lib/role";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { createClient } from "@/lib/supabase"; 
import { TreeItem } from "@/components/custom/TreeItem";
import {
  updateBusinessProcess,
  deleteBusinessProcess,
  updateControl,
  deleteControl,
  updateRisk,
  deleteRisk
} from "@/app/clientService";

// --- Types ---

interface OverviewControl {
  id: string;
  name: string;
  description?: string;
  type?: string;
}

interface OverviewRisk {
  id: string;
  name: string;
  description?: string;
  category?: string;
}

interface OverviewProcess {
  id: string;
  name: string;
  description?: string;
  controls: OverviewControl[];
  risks: OverviewRisk[];
}

interface OverviewResponse {
  processes: OverviewProcess[];
}

// --- Fetcher ---

const fetchOverviewData = async (): Promise<OverviewResponse> => {
  const supabase = createClient();
  const { data: { session } } = await supabase.auth.getSession();
  const token = session?.access_token;

  if (!token) {
    throw new Error("Not authenticated");
  }

  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/dashboard/overview`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!res.ok) {
    throw new Error("Failed to fetch overview data");
  }

  return res.json();
};

export default function OverviewPage() {
  const { isAdmin } = useRole();
  const queryClient = useQueryClient();
  
  const { data, isLoading, error } = useQuery({
    queryKey: ["overview"],
    queryFn: fetchOverviewData,
  });

  const [activeTab, setActiveTab] = useState("all");

  // Edit/Delete State
  const [editingItem, setEditingItem] = useState<{ type: 'process'|'control'|'risk', data: any } | null>(null);
  const [deletingItem, setDeletingItem] = useState<{ type: 'process'|'control'|'risk', id: string, name: string } | null>(null);
  const [formData, setFormData] = useState({ name: "", description: "" });

  // Mutations
  const updateProcessMutation = useMutation({
    mutationFn: (data: any) => updateBusinessProcess({ path: { process_id: data.id }, body: data.body }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["overview"] });
      toast.success("Process updated successfully");
      setEditingItem(null);
    }
  });

  const deleteProcessMutation = useMutation({
    mutationFn: (id: string) => deleteBusinessProcess({ path: { process_id: id } }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["overview"] });
      toast.success("Process deleted successfully");
      setDeletingItem(null);
    }
  });

  const updateControlMutation = useMutation({
    mutationFn: (data: any) => updateControl({ path: { control_id: data.id }, body: data.body }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["overview"] });
      toast.success("Control updated successfully");
      setEditingItem(null);
    }
  });

  const deleteControlMutation = useMutation({
    mutationFn: (id: string) => deleteControl({ path: { control_id: id } }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["overview"] });
      toast.success("Control deleted successfully");
      setDeletingItem(null);
    }
  });

  const updateRiskMutation = useMutation({
    mutationFn: (data: any) => updateRisk({ path: { risk_id: data.id }, body: data.body }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["overview"] });
      toast.success("Risk updated successfully");
      setEditingItem(null);
    }
  });

  const deleteRiskMutation = useMutation({
    mutationFn: (id: string) => deleteRisk({ path: { risk_id: id } }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["overview"] });
      toast.success("Risk deleted successfully");
      setDeletingItem(null);
    }
  });

  if (isLoading) {
    return (
      <div className="space-y-4 p-8">
        <Skeleton className="h-8 w-1/3" />
        <Skeleton className="h-[400px] w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>Failed to load overview data. Please try again later.</AlertDescription>
        </Alert>
      </div>
    );
  }

  const processes = data?.processes || [];

  const handleEdit = (type: 'process'|'control'|'risk', item: any) => {
    if (!isAdmin) return;
    setEditingItem({ type, data: item });
    setFormData({ name: item.name, description: item.description || "" });
  };

  const handleDelete = (type: 'process'|'control'|'risk', item: any) => {
    if (!isAdmin) return;
    setDeletingItem({ type, id: item.id, name: item.name });
  };

  const handleSave = () => {
    if (!editingItem) return;
    const { type, data } = editingItem;
    const body = { 
        name: formData.name, 
        description: formData.description,
        // Preserve other fields if needed, but for MVP we edit name/desc
    };

    if (type === 'process') updateProcessMutation.mutate({ id: data.id, body });
    else if (type === 'control') updateControlMutation.mutate({ id: data.id, body });
    else if (type === 'risk') updateRiskMutation.mutate({ id: data.id, body });
  };

  const handleDeleteConfirm = () => {
    if (!deletingItem) return;
    const { type, id } = deletingItem;

    if (type === 'process') deleteProcessMutation.mutate(id);
    else if (type === 'control') deleteControlMutation.mutate(id);
    else if (type === 'risk') deleteRiskMutation.mutate(id);
  };

  const ActionButtons = ({ type, item }: { type: 'process'|'control'|'risk', item: any }) => {
    if (!isAdmin) return null;
    return (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon" className="h-6 w-6" onClick={(e) => { e.stopPropagation(); handleEdit(type, item); }}>
          <Edit className="h-3 w-3" />
        </Button>
        <Button variant="ghost" size="icon" className="h-6 w-6 text-destructive hover:text-destructive" onClick={(e) => { e.stopPropagation(); handleDelete(type, item); }}>
          <Trash2 className="h-3 w-3" />
        </Button>
      </div>
    );
  };

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Compliance Overview</h2>
      </div>

      <Tabs defaultValue="all" value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="all">Tree View</TabsTrigger>
          <TabsTrigger value="processes">Processes</TabsTrigger>
          <TabsTrigger value="controls">Controls</TabsTrigger>
          <TabsTrigger value="risks">Risks</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Hierarchical View</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {processes.length === 0 && <p className="text-muted-foreground text-sm">No items found.</p>}
                {processes.map((proc) => (
                  <TreeItem 
                    key={proc.id} 
                    label={proc.name} 
                    icon={Settings} 
                    badgeCount={proc.controls.length + proc.risks.length}
                    actions={<ActionButtons type="process" item={proc} />}
                  >
                    {proc.controls.length > 0 && (
                      <TreeItem label="Controls" icon={Shield} defaultExpanded>
                        {proc.controls.map((ctrl) => (
                          <TreeItem 
                            key={ctrl.id} 
                            label={ctrl.name} 
                            icon={Shield} 
                            actions={<ActionButtons type="control" item={ctrl} />}
                          />
                        ))}
                      </TreeItem>
                    )}
                    {proc.risks.length > 0 && (
                      <TreeItem label="Risks" icon={AlertTriangle} defaultExpanded>
                        {proc.risks.map((risk) => (
                          <TreeItem 
                            key={risk.id} 
                            label={risk.name} 
                            icon={AlertTriangle} 
                            actions={<ActionButtons type="risk" item={risk} />}
                          />
                        ))}
                      </TreeItem>
                    )}
                  </TreeItem>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab: Processes */}
        <TabsContent value="processes" className="space-y-4">
          <Card>
            <CardHeader><CardTitle>Business Processes</CardTitle></CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {processes.map(p => (
                <Card key={p.id} className="border bg-card text-card-foreground shadow-sm">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">{p.name}</CardTitle>
                    <Settings className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-xs text-muted-foreground mt-1 line-clamp-2">{p.description}</div>
                  </CardContent>
                </Card>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab: Controls */}
        <TabsContent value="controls" className="space-y-4">
          <Card>
             <CardHeader><CardTitle>Controls</CardTitle></CardHeader>
             <CardContent className="space-y-2">
                {processes.flatMap(p => p.controls).map(c => (
                  <div key={c.id} className="flex items-center justify-between p-2 border rounded hover:bg-muted/50">
                    <div className="flex items-center gap-3">
                      <Shield className="h-4 w-4 text-green-600" />
                      <div>
                        <div className="font-medium text-sm">{c.name}</div>
                        <div className="text-xs text-muted-foreground">{c.type || 'Control'}</div>
                      </div>
                    </div>
                  </div>
                ))}
             </CardContent>
          </Card>
        </TabsContent>

        {/* Tab: Risks */}
        <TabsContent value="risks" className="space-y-4">
          <Card>
             <CardHeader><CardTitle>Risks</CardTitle></CardHeader>
             <CardContent className="space-y-2">
                {processes.flatMap(p => p.risks).map(r => (
                  <div key={r.id} className="flex items-center justify-between p-2 border rounded hover:bg-muted/50">
                    <div className="flex items-center gap-3">
                      <AlertTriangle className="h-4 w-4 text-red-500" />
                      <div>
                        <div className="font-medium text-sm">{r.name}</div>
                        <div className="text-xs text-muted-foreground">{r.category || 'Risk'}</div>
                      </div>
                    </div>
                  </div>
                ))}
             </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Edit Modal */}
      <Dialog open={!!editingItem} onOpenChange={(open) => !open && setEditingItem(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit {editingItem?.type === 'process' ? 'Process' : editingItem?.type === 'control' ? 'Control' : 'Risk'}</DialogTitle>
            <DialogDescription>Make changes to the item details here.</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">Name</Label>
              <Input 
                id="name" 
                value={formData.name} 
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="col-span-3" 
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="desc" className="text-right">Description</Label>
              <Textarea 
                id="desc" 
                value={formData.description} 
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="col-span-3" 
              />
            </div>
          </div>
          <DialogFooter>
            <Button onClick={handleSave} disabled={updateProcessMutation.isPending || updateControlMutation.isPending || updateRiskMutation.isPending}>
              Save changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Modal */}
      <Dialog open={!!deletingItem} onOpenChange={(open) => !open && setDeletingItem(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete {deletingItem?.type}?</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete <strong>{deletingItem?.name}</strong>? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeletingItem(null)}>Cancel</Button>
            <Button 
                variant="destructive" 
                onClick={handleDeleteConfirm}
                disabled={deleteProcessMutation.isPending || deleteControlMutation.isPending || deleteRiskMutation.isPending}
            >
                Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}