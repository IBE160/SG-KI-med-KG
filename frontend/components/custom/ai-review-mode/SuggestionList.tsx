import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

interface SuggestionListProps {
  suggestions: any[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export function SuggestionList({ suggestions, selectedId, onSelect }: SuggestionListProps) {
  if (!suggestions?.length) {
    return <div className="p-4 text-center text-muted-foreground">No pending suggestions.</div>;
  }

  return (
    <div className="flex flex-col h-full overflow-y-auto border-r">
      {suggestions.map((suggestion) => (
        <button
          key={suggestion.id}
          onClick={() => onSelect(suggestion.id)}
          className={cn(
            "flex flex-col items-start p-4 space-y-2 text-left transition-all hover:bg-accent",
            selectedId === suggestion.id ? "bg-accent border-l-4 border-primary pl-3" : ""
          )}
        >
          <div className="flex items-center justify-between w-full">
            <Badge variant={suggestion.type === "risk" ? "destructive" : "outline"}>
              {suggestion.type}
            </Badge>
            <span className="text-xs text-muted-foreground">
              Doc: {suggestion.document_id.slice(0, 8)}...
            </span>
          </div>
          <div className="text-sm font-medium line-clamp-2">
            {suggestion.content.description || "No description"}
          </div>
          <div className="text-xs text-muted-foreground line-clamp-1">
            Ref: {suggestion.source_reference}
          </div>
        </button>
      ))}
    </div>
  );
}
