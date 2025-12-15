"use client";

import { useState } from "react";
import { ChevronRight, ChevronDown } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface TreeItemProps {
  label: string;
  icon: any;
  children?: React.ReactNode;
  actions?: React.ReactNode;
  defaultExpanded?: boolean;
  badgeCount?: number;
}

export function TreeItem({ 
  label, 
  icon: Icon, 
  children, 
  actions, 
  defaultExpanded = false,
  badgeCount 
}: TreeItemProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const hasChildren = !!children;

  return (
    <div className="border-l border-border/50 ml-2 pl-2">
      <div className="flex items-center justify-between py-1 hover:bg-muted/50 rounded pr-2 group">
        <div 
          className="flex items-center gap-2 cursor-pointer flex-1" 
          onClick={() => hasChildren && setIsExpanded(!isExpanded)}
        >
          {hasChildren ? (
            isExpanded ? <ChevronDown className="h-4 w-4 text-muted-foreground" /> : <ChevronRight className="h-4 w-4 text-muted-foreground" />
          ) : (
            <div className="w-4" /> 
          )}
          <Icon className="h-4 w-4 text-primary" />
          <span className="font-medium text-sm">{label}</span>
          {badgeCount !== undefined && (
            <Badge variant="secondary" className="text-xs h-5 px-1.5 min-w-[1.25rem]">{badgeCount}</Badge>
          )}
        </div>
        <div className="opacity-0 group-hover:opacity-100 transition-opacity">
          {actions}
        </div>
      </div>
      {isExpanded && hasChildren && (
        <div className="ml-4 mt-1 space-y-1">
          {children}
        </div>
      )}
    </div>
  );
}
