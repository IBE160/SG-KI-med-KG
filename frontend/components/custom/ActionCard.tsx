import * as React from "react";
import Link from "next/link";
import * as LucideIcons from "lucide-react";
import { toast } from "sonner";

import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

interface ActionCardProps {
  title: string;
  metric: number;
  metricLabel: string;
  icon: string;
  actionLink: string;
  status?: "urgent" | "normal" | null;
  loading?: boolean;
}

/**
 * ActionCard - Reusable dashboard card component for Action-Oriented Hub
 *
 * Displays a key metric with an icon and CTA button linking to detailed view.
 * Supports skeleton loading state for async data fetching.
 */
export function ActionCard({
  title,
  metric,
  metricLabel,
  icon,
  actionLink,
  status,
  loading = false,
}: ActionCardProps) {
  // Dynamically load Lucide icon by name
  const IconComponent = (LucideIcons as any)[icon] || LucideIcons.Activity;

  const handleComingSoonClick = (e: React.MouseEvent) => {
    e.preventDefault();
    toast.info("Feature coming soon");
  };

  if (loading) {
    return (
      <Card className="hover:shadow-lg transition-shadow">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-4 w-4 rounded-full" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-8 w-16 mb-1" />
          <Skeleton className="h-4 w-24 mb-4" />
          <Skeleton className="h-9 w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      className={cn(
        "hover:shadow-lg transition-shadow",
        status === "urgent" && "border-red-500 border-l-4"
      )}
    >
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
        <IconComponent className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline gap-2 mb-1">
          <div className="text-3xl font-bold">{metric}</div>
          <span className="text-sm text-muted-foreground">{metricLabel}</span>
        </div>
        {status === "urgent" && (
          <p className="text-xs text-red-600 mb-3">Requires attention</p>
        )}
        {actionLink === "#coming-soon" ? (
          <div className="block mt-4">
            <Button variant="outline" className="w-full" onClick={handleComingSoonClick}>
              View
            </Button>
          </div>
        ) : (
          <Link href={actionLink} className="block mt-4">
            <Button variant="outline" className="w-full">
              View
            </Button>
          </Link>
        )}
      </CardContent>
    </Card>
  );
}
