"use client";

import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { ConnectionStatus } from "@/hooks/useRealtimeSubscription";

interface RealtimeStatusIndicatorProps {
  status: ConnectionStatus;
}

export function RealtimeStatusIndicator({
  status,
}: RealtimeStatusIndicatorProps) {
  const statusConfig = {
    connected: {
      color: "bg-green-500 hover:bg-green-600",
      text: "Connected",
      description: "Real-time updates active",
    },
    connecting: {
      color: "bg-yellow-500 hover:bg-yellow-600",
      text: "Connecting",
      description: "Establishing connection...",
    },
    disconnected: {
      color: "bg-red-500 hover:bg-red-600",
      text: "Disconnected",
      description: "Using fallback polling (60s)",
    },
  };

  const config = statusConfig[status];

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Badge
            className={`${config.color} text-white border-transparent cursor-help`}
          >
            <span className="mr-1.5">●</span>
            {config.text}
          </Badge>
        </TooltipTrigger>
        <TooltipContent>
          <p>{config.description}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
