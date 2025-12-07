"use client";

import { useEffect, useState, useCallback } from "react";
import { RealtimeChannel } from "@supabase/supabase-js";
import { createClient } from "@/lib/supabase";

export interface RealtimeChange {
  table: string;
  eventType: "INSERT" | "UPDATE" | "DELETE";
  new: Record<string, any>;
  old: Record<string, any>;
}

export type ConnectionStatus = "connected" | "connecting" | "disconnected";

export interface UseRealtimeSubscriptionParams {
  tableName: string;
  filterCriteria: { tenant_id: string };
  onEvent: (change: RealtimeChange) => void;
  enabled?: boolean;
}

export function useRealtimeSubscription({
  tableName,
  filterCriteria,
  onEvent,
  enabled = true,
}: UseRealtimeSubscriptionParams) {
  const [status, setStatus] = useState<ConnectionStatus>("connecting");
  const [channel, setChannel] = useState<RealtimeChannel | null>(null);

  const handleChange = useCallback(
    (payload: any) => {
      const change: RealtimeChange = {
        table: payload.table,
        eventType: payload.eventType,
        new: payload.new || {},
        old: payload.old || {},
      };
      onEvent(change);
    },
    [onEvent]
  );

  useEffect(() => {
    if (!enabled) {
      setStatus("disconnected");
      return;
    }

    const supabase = createClient();
    setStatus("connecting");

    // Create unique channel name for this subscription
    const channelName = `realtime:${tableName}:${filterCriteria.tenant_id}`;

    const realtimeChannel = supabase
      .channel(channelName)
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: tableName,
          filter: `tenant_id=eq.${filterCriteria.tenant_id}`,
        },
        handleChange
      )
      .subscribe((status) => {
        if (status === "SUBSCRIBED") {
          setStatus("connected");
        } else if (status === "CLOSED" || status === "CHANNEL_ERROR") {
          setStatus("disconnected");
        }
      });

    setChannel(realtimeChannel);

    // Cleanup function
    return () => {
      if (realtimeChannel) {
        supabase.removeChannel(realtimeChannel);
        setStatus("disconnected");
      }
    };
  }, [tableName, filterCriteria.tenant_id, handleChange, enabled]);

  return { status, channel };
}
