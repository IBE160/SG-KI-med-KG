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
import { Input } from "@/components/ui/input";
import { Upload, FileText, MoreVertical, Trash2, Edit2, Download, Info, RefreshCw, X, Play, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { createClient } from "@/lib/supabase";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface Document {
  id: string;
  filename: string;
  status: "pending" | "processing" | "completed" | "failed";
  created_at: string;
  classification?: {
    document_type: string;
    framework_name: string;
    parent_law_name?: string;
  };
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState<Document | null>(null);
  const [renameDialogOpen, setRenameDialogOpen] = useState(false);
  const [documentToRename, setDocumentToRename] = useState<Document | null>(null);
  const [newFilename, setNewFilename] = useState("");
  const [processingDocId, setProcessingDocId] = useState<string | null>(null);
  const supabase = createClient();

  const fetchDocuments = async () => {
    try {
      setLoading(true);

      // Get auth token
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) {
        toast.error("Not authenticated");
        return;
      }

      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/v1/documents`, {
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch documents");
      }

      const data = await response.json();
      setDocuments(data);
    } catch (err) {
      console.error("Failed to fetch documents:", err);
      toast.error("Failed to load documents");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      const validTypes = ["application/pdf", "text/plain"];
      if (!validTypes.includes(file.type)) {
        toast.error("Only PDF and text files are allowed");
        return;
      }

      // Validate file size (20MB)
      const maxSize = 20 * 1024 * 1024;
      if (file.size > maxSize) {
        toast.error("File size must be less than 20MB");
        return;
      }

      setSelectedFile(file);
    }
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    const fileInput = document.getElementById("file-upload") as HTMLInputElement;
    if (fileInput) fileInput.value = "";
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error("Please select a file first");
      return;
    }

    try {
      setUploading(true);

      // Get auth token
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) {
        toast.error("Not authenticated");
        return;
      }

      const formData = new FormData();
      formData.append("file", selectedFile);

      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/v1/documents/upload`, {
        method: "POST",
        body: formData,
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Upload failed");
      }

      const result = await response.json();
      toast.success(result.message || "File uploaded successfully");

      // Add new document to state immediately
      const newDocument: Document = {
        id: result.id,
        filename: result.filename,
        status: result.status,
        created_at: new Date().toISOString(),
      };
      setDocuments(prevDocs => [newDocument, ...prevDocs]);

      // Clear selection
      setSelectedFile(null);
      const fileInput = document.getElementById(
        "file-upload"
      ) as HTMLInputElement;
      if (fileInput) fileInput.value = "";
    } catch (err) {
      console.error("Upload failed:", err);
      toast.error(
        err instanceof Error ? err.message : "Failed to upload file"
      );
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteClick = (doc: Document) => {
    setDocumentToDelete(doc);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!documentToDelete) return;

    const doc = documentToDelete;

    // Close dialog immediately - no waiting for animations
    setDeleteDialogOpen(false);
    setDocumentToDelete(null);

    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) {
        toast.error("Not authenticated");
        return;
      }

      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/v1/documents/${doc.id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("Delete error:", response.status, errorData);
        throw new Error(errorData.detail || "Failed to delete document");
      }

      // Remove document from state immediately
      setDocuments(prevDocs => prevDocs.filter(d => d.id !== doc.id));

      toast.success("Document archived successfully");
    } catch (err) {
      console.error("Delete failed:", err);
      toast.error(err instanceof Error ? err.message : "Failed to delete document");
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setDocumentToDelete(null);
  };

  const handleDownload = (doc: Document) => {
    toast.info("Download feature coming soon");
    // TODO: Implement download endpoint
  };

  const handleRenameClick = (doc: Document) => {
    setDocumentToRename(doc);
    // Pre-fill with current filename (without extension for easier editing)
    const nameWithoutExt = doc.filename.replace(/\.[^/.]+$/, "");
    setNewFilename(nameWithoutExt);
    setRenameDialogOpen(true);
  };

  const handleRenameConfirm = async () => {
    if (!documentToRename || !newFilename.trim()) return;

    const doc = documentToRename;
    const filename = newFilename.trim();

    // Close dialog immediately
    setRenameDialogOpen(false);
    setDocumentToRename(null);
    setNewFilename("");

    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) {
        toast.error("Not authenticated");
        return;
      }

      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(
        `${backendUrl}/api/v1/documents/${doc.id}/rename`,
        {
          method: "PATCH",
          headers: {
            Authorization: `Bearer ${session.access_token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ new_filename: filename }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to rename document");
      }

      const updatedDoc = await response.json();

      // Update document in state immediately
      setDocuments(prevDocs =>
        prevDocs.map(d => (d.id === doc.id ? { ...d, filename: updatedDoc.filename } : d))
      );

      toast.success("Document renamed successfully");
    } catch (err) {
      console.error("Rename failed:", err);
      toast.error(err instanceof Error ? err.message : "Failed to rename document");
    }
  };

  const handleRenameCancel = () => {
    setRenameDialogOpen(false);
    setDocumentToRename(null);
    setNewFilename("");
  };

  const handleViewDetails = (doc: Document) => {
    toast.info("Details view coming soon");
    // TODO: Implement details dialog
  };

  const handleReprocess = async (doc: Document) => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) {
        toast.error("Not authenticated");
        return;
      }

      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/v1/documents/${doc.id}/reprocess`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to reprocess document");
      }

      toast.success("Document queued for reprocessing");
      fetchDocuments();
    } catch (err) {
      console.error("Reprocess failed:", err);
      toast.error("Failed to reprocess document");
    }
  };

  const handleProcess = async (doc: Document) => {
    try {
      setProcessingDocId(doc.id);

      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) {
        toast.error("Not authenticated");
        return;
      }

      toast.info("Processing document... This may take a minute.");

      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/v1/documents/${doc.id}/process`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to process document");
      }

      const result = await response.json();
      toast.success(result.message || "Document processed successfully");

      // Update document status in state
      setDocuments(prevDocs =>
        prevDocs.map(d => (d.id === doc.id ? { ...d, status: result.status || "completed" } : d))
      );
    } catch (err) {
      console.error("Process failed:", err);
      toast.error(err instanceof Error ? err.message : "Failed to process document");
    } finally {
      setProcessingDocId(null);
    }
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    return `${day}/${month}/${year}, ${hours}:${minutes}:${seconds}`;
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      pending: "bg-yellow-100 text-yellow-800",
      processing: "bg-blue-100 text-blue-800",
      completed: "bg-green-100 text-green-800",
      failed: "bg-red-100 text-red-800",
    };

    return (
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          styles[status as keyof typeof styles] || ""
        }`}
      >
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Documents</h1>
        <p className="text-muted-foreground">
          Upload regulatory documents for AI analysis
        </p>
      </div>

      {/* Upload Section */}
      <div className="border rounded-lg p-6 bg-card">
        <h2 className="text-lg font-semibold mb-4">Upload Document</h2>
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <div className="flex-1 flex items-center gap-2">
              <Input
                id="file-upload"
                type="file"
                accept=".pdf,.txt"
                onChange={handleFileSelect}
                disabled={uploading}
                className="flex-1"
              />
              {selectedFile && !uploading && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleClearFile}
                  className="h-10 w-10 shrink-0"
                  title="Clear selected file"
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
            <Button
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              className="min-w-[120px]"
            >
              {uploading ? (
                "Uploading..."
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload
                </>
              )}
            </Button>
          </div>
          <p className="text-sm text-muted-foreground">
            Supported formats: PDF, TXT (max 20MB)
          </p>
        </div>
      </div>

      {/* Documents List */}
      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Filename</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Classification</TableHead>
              <TableHead>Uploaded</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-10">
                  Loading...
                </TableCell>
              </TableRow>
            ) : documents.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={5}
                  className="text-center py-10 text-muted-foreground"
                >
                  <div className="flex flex-col items-center gap-2">
                    <FileText className="h-12 w-12 text-muted-foreground/50" />
                    <p>No documents uploaded yet</p>
                    <p className="text-sm">
                      Upload a document to get started with AI analysis
                    </p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              documents.map((doc) => (
                <TableRow key={doc.id}>
                  <TableCell className="font-medium">{doc.filename}</TableCell>
                  <TableCell>{getStatusBadge(doc.status)}</TableCell>
                  <TableCell> {/* New Cell for Classification */}
                    {doc.classification ? (
                      <div className="flex flex-col text-xs">
                        <span>Type: {doc.classification.document_type}</span>
                        <span>Name: {doc.classification.framework_name}</span>
                        {doc.classification.parent_law_name && (
                          <span>Parent: {doc.classification.parent_law_name}</span>
                        )}
                      </div>
                    ) : (
                      "N/A"
                    )}
                  </TableCell>
                  <TableCell>
                    {formatDateTime(doc.created_at)}
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleDownload(doc)}>
                          <Download className="mr-2 h-4 w-4" />
                          Download
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleViewDetails(doc)}>
                          <Info className="mr-2 h-4 w-4" />
                          View Details
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleRenameClick(doc)}>
                          <Edit2 className="mr-2 h-4 w-4" />
                          Rename
                        </DropdownMenuItem>
                        {(doc.status === "pending" || doc.status === "failed") && (
                          <DropdownMenuItem
                            onClick={() => handleProcess(doc)}
                            disabled={processingDocId === doc.id}
                          >
                            {processingDocId === doc.id ? (
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            ) : (
                              <Play className="mr-2 h-4 w-4" />
                            )}
                            {processingDocId === doc.id ? "Processing..." : "Process Now"}
                          </DropdownMenuItem>
                        )}
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          onClick={() => handleDeleteClick(doc)}
                          className="text-red-600 focus:text-red-600"
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Custom Delete Confirmation Dialog */}
      {deleteDialogOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/80"
            onClick={handleDeleteCancel}
          />

          {/* Dialog */}
          <div className="relative bg-background border rounded-lg shadow-lg p-6 w-full max-w-lg mx-4">
            <h2 className="text-lg font-semibold mb-2">Archive Document</h2>
            <p className="text-sm text-muted-foreground mb-6">
              Are you sure you want to archive &quot;{documentToDelete?.filename}&quot;?
              The document will be moved to archive and can be restored later.
            </p>
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={handleDeleteCancel}
              >
                Cancel
              </Button>
              <Button
                type="button"
                onClick={handleDeleteConfirm}
                className="bg-red-600 hover:bg-red-700"
              >
                Archive
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Rename Dialog */}
      {renameDialogOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/80"
            onClick={handleRenameCancel}
          />

          {/* Dialog */}
          <div className="relative bg-background border rounded-lg shadow-lg p-6 w-full max-w-lg mx-4">
            <h2 className="text-lg font-semibold mb-2">Rename Document</h2>
            <p className="text-sm text-muted-foreground mb-4">
              Enter a new name for &quot;{documentToRename?.filename}&quot;. The file extension will be preserved automatically.
            </p>
            <Input
              type="text"
              value={newFilename}
              onChange={(e) => setNewFilename(e.target.value)}
              placeholder="Enter new filename"
              className="mb-6"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleRenameConfirm();
                } else if (e.key === "Escape") {
                  handleRenameCancel();
                }
              }}
            />
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={handleRenameCancel}
              >
                Cancel
              </Button>
              <Button
                type="button"
                onClick={handleRenameConfirm}
                disabled={!newFilename.trim()}
              >
                Rename
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
