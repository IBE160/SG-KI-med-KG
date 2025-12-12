"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChevronRight, ChevronLeft, Search } from "lucide-react";
import { cn } from "@/lib/utils";

export interface DualListItem {
  id: string;
  name: string;
}

interface DualListSelectorProps {
  availableItems: DualListItem[];
  selectedItems: DualListItem[];
  onSelectionChange: (selectedIds: string[]) => void;
  availableTitle?: string;
  selectedTitle?: string;
  className?: string;
}

/**
 * DualListSelector - Reusable component for selecting items between two lists
 *
 * Displays available items on the left and selected items on the right,
 * with transfer buttons to move items between lists. Supports search filtering
 * and keyboard navigation.
 */
export function DualListSelector({
  availableItems,
  selectedItems,
  onSelectionChange,
  availableTitle = "Available Items",
  selectedTitle = "Selected Items",
  className,
}: DualListSelectorProps) {
  const [availableSearch, setAvailableSearch] = React.useState("");
  const [selectedSearch, setSelectedSearch] = React.useState("");
  const [selectedAvailableIds, setSelectedAvailableIds] = React.useState<
    Set<string>
  >(new Set());
  const [selectedSelectedIds, setSelectedSelectedIds] = React.useState<
    Set<string>
  >(new Set());

  // Filter items based on search
  const filteredAvailable = availableItems.filter((item) =>
    item.name.toLowerCase().includes(availableSearch.toLowerCase())
  );

  const filteredSelected = selectedItems.filter((item) =>
    item.name.toLowerCase().includes(selectedSearch.toLowerCase())
  );

  // Handle adding items (available -> selected)
  const handleAdd = () => {
    if (selectedAvailableIds.size === 0) return;

    const newSelectedIds = [
      ...selectedItems.map((item) => item.id),
      ...Array.from(selectedAvailableIds),
    ];

    onSelectionChange(newSelectedIds);
    setSelectedAvailableIds(new Set());
  };

  // Handle removing items (selected -> available)
  const handleRemove = () => {
    if (selectedSelectedIds.size === 0) return;

    const newSelectedIds = selectedItems
      .filter((item) => !selectedSelectedIds.has(item.id))
      .map((item) => item.id);

    onSelectionChange(newSelectedIds);
    setSelectedSelectedIds(new Set());
  };

  // Toggle item selection in available list
  const toggleAvailableItem = (id: string) => {
    const newSet = new Set(selectedAvailableIds);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setSelectedAvailableIds(newSet);
  };

  // Toggle item selection in selected list
  const toggleSelectedItem = (id: string) => {
    const newSet = new Set(selectedSelectedIds);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setSelectedSelectedIds(newSet);
  };

  // Keyboard navigation support
  const handleAvailableKeyDown = (
    e: React.KeyboardEvent,
    id: string,
    index: number
  ) => {
    if (e.key === " " || e.key === "Enter") {
      e.preventDefault();
      toggleAvailableItem(id);
    } else if (e.key === "ArrowRight" && selectedAvailableIds.has(id)) {
      e.preventDefault();
      handleAdd();
    }
  };

  const handleSelectedKeyDown = (
    e: React.KeyboardEvent,
    id: string,
    index: number
  ) => {
    if (e.key === " " || e.key === "Enter") {
      e.preventDefault();
      toggleSelectedItem(id);
    } else if (e.key === "ArrowLeft" && selectedSelectedIds.has(id)) {
      e.preventDefault();
      handleRemove();
    }
  };

  return (
    <div className={cn("grid grid-cols-[1fr_auto_1fr] gap-4", className)}>
      {/* Available Items List */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">{availableTitle}</CardTitle>
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search..."
              value={availableSearch}
              onChange={(e) => setAvailableSearch(e.target.value)}
              className="pl-8"
            />
          </div>
        </CardHeader>
        <CardContent>
          <div className="border rounded-md min-h-[300px] max-h-[400px] overflow-y-auto">
            {filteredAvailable.length === 0 ? (
              <div className="p-4 text-center text-sm text-muted-foreground">
                No items available
              </div>
            ) : (
              <div className="divide-y">
                {filteredAvailable.map((item, index) => (
                  <div
                    key={item.id}
                    role="button"
                    tabIndex={0}
                    className={cn(
                      "p-3 cursor-pointer hover:bg-accent transition-colors",
                      selectedAvailableIds.has(item.id) && "bg-accent"
                    )}
                    onClick={() => toggleAvailableItem(item.id)}
                    onKeyDown={(e) => handleAvailableKeyDown(e, item.id, index)}
                  >
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={selectedAvailableIds.has(item.id)}
                        onChange={() => toggleAvailableItem(item.id)}
                        onClick={(e) => e.stopPropagation()}
                        className="cursor-pointer"
                      />
                      <span className="text-sm">{item.name}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="mt-2 text-xs text-muted-foreground">
            {filteredAvailable.length} items
          </div>
        </CardContent>
      </Card>

      {/* Transfer Buttons */}
      <div className="flex flex-col items-center justify-center gap-2">
        <Button
          onClick={handleAdd}
          disabled={selectedAvailableIds.size === 0}
          variant="outline"
          size="icon"
          title="Add selected items"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
        <Button
          onClick={handleRemove}
          disabled={selectedSelectedIds.size === 0}
          variant="outline"
          size="icon"
          title="Remove selected items"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
      </div>

      {/* Selected Items List */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">{selectedTitle}</CardTitle>
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search..."
              value={selectedSearch}
              onChange={(e) => setSelectedSearch(e.target.value)}
              className="pl-8"
            />
          </div>
        </CardHeader>
        <CardContent>
          <div className="border rounded-md min-h-[300px] max-h-[400px] overflow-y-auto">
            {filteredSelected.length === 0 ? (
              <div className="p-4 text-center text-sm text-muted-foreground">
                No items selected
              </div>
            ) : (
              <div className="divide-y">
                {filteredSelected.map((item, index) => (
                  <div
                    key={item.id}
                    role="button"
                    tabIndex={0}
                    className={cn(
                      "p-3 cursor-pointer hover:bg-accent transition-colors",
                      selectedSelectedIds.has(item.id) && "bg-accent"
                    )}
                    onClick={() => toggleSelectedItem(item.id)}
                    onKeyDown={(e) => handleSelectedKeyDown(e, item.id, index)}
                  >
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={selectedSelectedIds.has(item.id)}
                        onChange={() => toggleSelectedItem(item.id)}
                        onClick={(e) => e.stopPropagation()}
                        className="cursor-pointer"
                      />
                      <span className="text-sm">{item.name}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="mt-2 text-xs text-muted-foreground">
            {filteredSelected.length} items
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
