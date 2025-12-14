"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { listSuggestions } from "@/app/clientService";
import type { AISuggestionRead, SuggestionType } from "@/app/openapi-client/types.gen";
import { FileText, AlertCircle, Shield, Briefcase, ArrowUpDown, Search, X } from "lucide-react";
import { createClient } from "@/lib/supabase";
import { ReviewSuggestionDialog } from "@/components/custom/review-suggestion/ReviewSuggestionDialog";
import React, { useState, useMemo } from "react";


export default function AdminSuggestionsPage() {
  const router = useRouter();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState<AISuggestionRead | null>(null);
  
  // Sorting and Filtering State
  const [filterStatus, setFilterStatus] = useState<string>("pending");
  const [filterType, setFilterType] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [sortConfig, setSortConfig] = useState<{ key: keyof AISuggestionRead | "name" | "assigned_to"; direction: "asc" | "desc" } | null>(null);

  const { data: suggestions, isLoading, error, refetch } = useQuery<AISuggestionRead[]>({
    queryKey: ["/api/v1/suggestions", filterStatus],
    queryFn: async () => {
      try {
        const supabase = createClient();
        const { data: { session } } = await supabase.auth.getSession();
        const token = session?.access_token;

        const response = await listSuggestions({
          query: filterStatus === "all" ? {} : {
            status: filterStatus as any,
          },
          headers: token ? {
            Authorization: `Bearer ${token}`,
          } : undefined,
        });
        if (response.error) {
          console.error("API error details:", response.error);
          throw new Error(`API Error: ${JSON.stringify(response.error)}`);
        }
        return response.data || [];
      } catch (err) {
        console.error("Fetch error:", err);
        throw err;
      }
    },
    retry: false,
    refetchOnWindowFocus: false,
  });

  const handleReviewClick = (suggestion: AISuggestionRead) => {
    setSelectedSuggestion(suggestion);
    setIsDialogOpen(true);
  };

  const handleDialogSuccess = () => {
    refetch(); // Re-fetch suggestions after an action
    setSelectedSuggestion(null);
  };

  const handleSort = (key: keyof AISuggestionRead | "name" | "assigned_to") => {
    let direction: "asc" | "desc" = "asc";
    if (sortConfig && sortConfig.key === key && sortConfig.direction === "asc") {
      direction = "desc";
    }
    setSortConfig({ key, direction });
  };

  const getContentSummary = (content: { [key: string]: unknown }, type: string): string => {
    // Standardize name extraction
    return (content.name as string) || 
           (content.risk_name as string) || 
           (content.control_name as string) || 
           (content.process_name as string) ||
           `Unnamed ${type}`;
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "risk":
        return <AlertCircle className="h-4 w-4 text-orange-600" />;
      case "control":
        return <Shield className="h-4 w-4 text-blue-600" />;
      case "business_process":
        return <Briefcase className="h-4 w-4 text-purple-600" />;
      default:
        return <FileText className="h-4 w-4 text-gray-600" />;
    }
  };

  const getTypeBadge = (type: string) => {
    switch (type) {
      case "risk":
        return <Badge variant="destructive">Risk</Badge>;
      case "control":
        return <Badge variant="default">Control</Badge>; // Default implies primary/blue-ish
      case "business_process":
        return <Badge variant="outline" className="border-purple-500 text-purple-600">Process</Badge>;
      default:
        return <Badge variant="secondary">{type}</Badge>;
    }
  };

  const processedSuggestions = useMemo(() => {
    if (!suggestions) return [];

    let result = [...suggestions];

    // Filter by type
    if (filterType !== "all") {
      result = result.filter((s) => s.type === filterType);
    }

    // Filter by name/title search
    if (searchTerm.trim()) {
      const lowerSearch = searchTerm.toLowerCase();
      result = result.filter((s) => {
        const name = getContentSummary(s.content, s.type).toLowerCase();
        return name.includes(lowerSearch);
      });
    }

    // Sort
    if (sortConfig) {
      result.sort((a, b) => {
        let aValue: any = "";
        let bValue: any = "";

        if (sortConfig.key === "name") {
            aValue = getContentSummary(a.content, a.type).toLowerCase();
            bValue = getContentSummary(b.content, b.type).toLowerCase();
        } else if (sortConfig.key === "assigned_to") {
            aValue = a.assigned_bpo?.full_name || a.assigned_bpo?.email || "zzz_unassigned";
            bValue = b.assigned_bpo?.full_name || b.assigned_bpo?.email || "zzz_unassigned";
        } else {
            aValue = a[sortConfig.key];
            bValue = b[sortConfig.key];
        }

        if (aValue < bValue) return sortConfig.direction === "asc" ? -1 : 1;
        if (aValue > bValue) return sortConfig.direction === "asc" ? 1 : -1;
        return 0;
      });
    }

    return result;
  }, [suggestions, filterType, searchTerm, sortConfig]);

  if (isLoading) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-6">Pending AI Suggestions</h1>
        <div className="space-y-4">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-6">Pending AI Suggestions</h1>
        <div className="p-4 border border-red-500 bg-red-50 text-red-900 rounded">
          <p className="font-semibold mb-2">Failed to load suggestions:</p>
          <pre className="text-sm overflow-auto">
            {error instanceof Error ? error.message : JSON.stringify(error, null, 2)}
          </pre>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-2xl font-bold">AI Suggestions</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Review and manage AI-generated suggestions from document analysis
            </p>
          </div>
          <div className="flex items-center gap-2 text-sm font-medium text-gray-600">
            <FileText className="h-5 w-5 text-muted-foreground" />
            <span>{suggestions?.length || 0} total</span>
            <span className="text-muted-foreground">•</span>
            <span>{processedSuggestions.length} shown</span>
          </div>
        </div>

        {/* Status Filter Tabs */}
        <div className="flex items-center gap-2 mb-4 border-b pb-3">
          <span className="text-sm font-medium text-muted-foreground">Status:</span>
          <div className="flex gap-2">
            <Button
              variant={filterStatus === "all" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilterStatus("all")}
            >
              All
            </Button>
            <Button
              variant={filterStatus === "pending" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilterStatus("pending")}
            >
              Pending
            </Button>
            <Button
              variant={filterStatus === "pending_review" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilterStatus("pending_review")}
            >
              Pending Review
            </Button>
            <Button
              variant={filterStatus === "active" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilterStatus("active")}
            >
              Active
            </Button>
            <Button
              variant={filterStatus === "rejected" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilterStatus("rejected")}
            >
              Rejected
            </Button>
            <Button
              variant={filterStatus === "archived" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilterStatus("archived")}
            >
              Archived
            </Button>
          </div>
        </div>

        {/* Filter and Search Toolbar */}
        <div className="flex items-center gap-4 mb-4">
          {/* Search Input */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search by name or title..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-9"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm("")}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>

          {/* Type Filter Chips */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Type:</span>
            <div className="flex gap-2">
              <Button
                variant={filterType === "all" ? "default" : "outline"}
                size="sm"
                onClick={() => setFilterType("all")}
              >
                All
              </Button>
              <Button
                variant={filterType === "risk" ? "default" : "outline"}
                size="sm"
                onClick={() => setFilterType(filterType === "risk" ? "all" : "risk")}
              >
                Risk
              </Button>
              <Button
                variant={filterType === "control" ? "default" : "outline"}
                size="sm"
                onClick={() => setFilterType(filterType === "control" ? "all" : "control")}
              >
                Control
              </Button>
              <Button
                variant={filterType === "business_process" ? "default" : "outline"}
                size="sm"
                onClick={() => setFilterType(filterType === "business_process" ? "all" : "business_process")}
              >
                Process
              </Button>
            </div>
          </div>
        </div>

        {/* Active Filters Badge */}
        {searchTerm && (
          <div className="flex items-center gap-2 mb-2">
            <Badge variant="secondary" className="flex items-center gap-1">
              Searching for: &quot;{searchTerm}&quot;
              <button onClick={() => setSearchTerm("")} className="ml-1 hover:text-foreground">
                <X className="h-3 w-3" />
              </button>
            </Badge>
          </div>
        )}
      </div>

      {Array.isArray(processedSuggestions) && processedSuggestions.length > 0 ? (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[120px] cursor-pointer hover:bg-muted/50" onClick={() => handleSort("type")}>
                  Type <ArrowUpDown className="ml-2 h-4 w-4 inline" />
              </TableHead>
              <TableHead className="cursor-pointer hover:bg-muted/50" onClick={() => handleSort("name")}>
                  Name <ArrowUpDown className="ml-2 h-4 w-4 inline" />
              </TableHead>
              <TableHead>Rationale</TableHead>
              <TableHead>Source Reference</TableHead>
              <TableHead className="cursor-pointer hover:bg-muted/50" onClick={() => handleSort("status")}>
                  Status <ArrowUpDown className="ml-2 h-4 w-4 inline" />
              </TableHead>
              <TableHead className="cursor-pointer hover:bg-muted/50" onClick={() => handleSort("assigned_to")}>
                  Assigned To <ArrowUpDown className="ml-2 h-4 w-4 inline" />
              </TableHead>
              <TableHead className="text-right">Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {processedSuggestions.map((suggestion) => (
              <TableRow
                key={suggestion.id}
                className="cursor-pointer hover:bg-gray-50"
              >
                <TableCell>
                  <div className="flex items-center gap-2">
                    {getTypeIcon(suggestion.type)}
                    {getTypeBadge(suggestion.type)}
                  </div>
                </TableCell>
                <TableCell className="font-medium max-w-xs">
                  <div className="truncate">
                    {getContentSummary(suggestion.content, suggestion.type)}
                  </div>
                </TableCell>
                <TableCell className="max-w-md">
                  <div className="text-sm text-gray-600 line-clamp-2">
                    {suggestion.rationale}
                  </div>
                </TableCell>
                <TableCell className="max-w-xs">
                  <div className="text-sm text-gray-500 truncate">
                    {suggestion.source_reference}
                  </div>
                </TableCell>
                <TableCell>
                  <Badge variant={
                    suggestion.status === "pending" ? "secondary" :
                    suggestion.status === "pending_review" ? "default" :
                    suggestion.status === "active" ? "outline" :
                    suggestion.status === "archived" ? "secondary" :
                    "destructive"
                  }>
                    {suggestion.status === "pending_review" ? "Pending Review" :
                     suggestion.status.charAt(0).toUpperCase() + suggestion.status.slice(1)}
                  </Badge>
                </TableCell>
                <TableCell>
                  {suggestion.assigned_bpo ? (
                    <div className="flex items-center gap-1">
                      <span className="text-sm font-medium">
                        {suggestion.assigned_bpo.full_name || suggestion.assigned_bpo.email}
                      </span>
                    </div>
                  ) : (
                    <span className="text-sm text-muted-foreground italic">Unassigned</span>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  {(suggestion.status === "pending" || suggestion.status === "pending_review") && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleReviewClick(suggestion)}
                    >
                      {suggestion.status === "pending_review" ? "Approve/Reject" : "Review"}
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      ) : (
        <div className="p-12 text-center border-2 border-dashed border-gray-300 rounded-lg">
          <FileText className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No pending suggestions matching criteria
          </h3>
          <p className="text-sm text-gray-600">
            Clear filters or upload a new document to generate suggestions.
          </p>
        </div>
      )}

      {selectedSuggestion && (
        <ReviewSuggestionDialog
          suggestion={selectedSuggestion}
          isOpen={isDialogOpen}
          onOpenChange={setIsDialogOpen}
          onSuccess={handleDialogSuccess}
        />
      )}
    </div>
  );
}