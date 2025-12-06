import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Check, X, Edit2 } from "lucide-react";
import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";

interface SuggestionDetailProps {
  suggestion: any;
  bpoUsers: any[];
  onAccept: (content?: any, bpoId?: string) => void;
  onReject: () => void;
}

export function SuggestionDetail({ suggestion, bpoUsers, onAccept, onReject }: SuggestionDetailProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(suggestion?.content);
  const [selectedBPO, setSelectedBPO] = useState<string>("");

  if (!suggestion) {
    return (
      <div className="flex h-full items-center justify-center text-muted-foreground">
        Select a suggestion to review
      </div>
    );
  }

  const handleSave = () => {
    setIsEditing(false);
    // Logic to persist edit locally before accept could go here if needed
  };

  const handleContentChange = (key: string, value: string) => {
    setEditedContent((prev: any) => ({ ...prev, [key]: value }));
  };

  const handleAcceptClick = () => {
    if (!selectedBPO) {
      toast.error("Please select a BPO for final approval");
      return;
    }
    onAccept(isEditing ? editedContent : undefined, selectedBPO);
    setSelectedBPO(""); // Reset after accept
  };

  return (
    <div className="flex flex-col h-full p-6 space-y-6 overflow-y-auto">
      <div className="flex justify-between items-start">
        <div>
          <Badge variant={suggestion.type === "risk" ? "destructive" : "default"} className="mb-2">
            {suggestion.type.toUpperCase()}
          </Badge>
          <h2 className="text-2xl font-bold tracking-tight">Suggestion Review</h2>
        </div>
        <div className="flex space-x-2 items-center">
          <div className="w-[200px]">
            <Select value={selectedBPO} onValueChange={setSelectedBPO}>
              <SelectTrigger>
                <SelectValue placeholder="Assign BPO" />
              </SelectTrigger>
              <SelectContent>
                {bpoUsers.map((user) => (
                  <SelectItem key={user.id} value={user.id}>
                    {user.email}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button variant="outline" onClick={onReject}>
            <X className="mr-2 h-4 w-4" />
            Reject
          </Button>
          <Button onClick={handleAcceptClick}>
            <Check className="mr-2 h-4 w-4" />
            Accept
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Content</CardTitle>
          <Button variant="ghost" size="sm" onClick={() => setIsEditing(!isEditing)}>
            <Edit2 className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent>
          {isEditing ? (
            <div className="space-y-4 pt-4">
              {Object.entries(editedContent || {}).map(([key, value]) => (
                <div key={key} className="grid w-full gap-1.5">
                  <Label htmlFor={key} className="capitalize">{key.replace(/_/g, " ")}</Label>
                  <Textarea 
                    id={key} 
                    value={value as string} 
                    onChange={(e) => handleContentChange(key, e.target.value)} 
                  />
                </div>
              ))}
              <Button size="sm" onClick={handleSave}>Done Editing</Button>
            </div>
          ) : (
            <dl className="grid grid-cols-1 gap-4 pt-4 sm:grid-cols-2">
              {Object.entries(suggestion.content || {}).map(([key, value]) => (
                <div key={key}>
                  <dt className="text-sm font-medium text-muted-foreground capitalize">
                    {key.replace(/_/g, " ")}
                  </dt>
                  <dd className="text-sm mt-1">{value as React.ReactNode}</dd>
                </div>
              ))}
            </dl>
          )}
        </CardContent>
      </Card>

      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold mb-2">Rationale</h3>
          <p className="text-muted-foreground leading-relaxed">
            {suggestion.rationale}
          </p>
        </div>
        <Separator />
        <div>
          <h3 className="text-lg font-semibold mb-2">Source Reference</h3>
          <div className="bg-muted p-4 rounded-md font-mono text-sm">
            {suggestion.source_reference}
          </div>
        </div>
      </div>
    </div>
  );
}
