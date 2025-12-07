/**
 * Integration tests for Realtime subscriptions in Dashboard page
 * Story 4-2: Real-Time Status Updates
 */

import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Use manual mock for @/lib/supabase
jest.mock("@/lib/supabase");

// Import components and mocked supabase
import DashboardPage from "@/app/(dashboard)/page";
import * as SupabaseLib from "@/lib/supabase";

const createClient = jest.mocked(SupabaseLib.createClient);

describe("Dashboard Realtime Integration", () => {
  let mockChannel: any;
  let mockSupabase: any;
  let queryClient: QueryClient;
  let capturedEventHandlers: Map<string, any>;

  beforeEach(() => {
    capturedEventHandlers = new Map();

    mockChannel = {
      on: jest.fn().mockImplementation((eventType, config, handler) => {
        capturedEventHandlers.set(config.table, handler);
        return mockChannel;
      }),
      subscribe: jest.fn().mockImplementation((callback) => {
        setTimeout(() => callback("SUBSCRIBED"), 0);
        return mockChannel;
      }),
    };

    mockSupabase = {
      channel: jest.fn().mockReturnValue(mockChannel),
      removeChannel: jest.fn(),
    };

    createClient.mockReturnValue(mockSupabase as any);

    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
    queryClient.clear();
  });

  const renderDashboard = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <DashboardPage />
      </QueryClientProvider>
    );
  };

  it("establishes Realtime subscriptions to all 3 tables on mount", async () => {
    renderDashboard();

    await waitFor(() => {
      expect(mockSupabase.channel).toHaveBeenCalledWith(
        expect.stringContaining("realtime:controls:")
      );
      expect(mockSupabase.channel).toHaveBeenCalledWith(
        expect.stringContaining("realtime:risks:")
      );
      expect(mockSupabase.channel).toHaveBeenCalledWith(
        expect.stringContaining("realtime:business_processes:")
      );
    });

    expect(mockChannel.subscribe).toHaveBeenCalledTimes(3);
  });

  it("invalidates React Query cache when controls Realtime event received", async () => {
    const invalidateSpy = jest.spyOn(queryClient, "invalidateQueries");

    renderDashboard();

    // Wait for subscriptions to establish
    await waitFor(() => {
      expect(capturedEventHandlers.has("controls")).toBe(true);
    });

    // Simulate INSERT event from Supabase
    const mockPayload = {
      table: "controls",
      eventType: "INSERT",
      new: { id: 1, name: "New Control", tenant_id: "demo-tenant-id" },
      old: {},
    };

    const controlsHandler = capturedEventHandlers.get("controls");
    controlsHandler(mockPayload);

    await waitFor(() => {
      expect(invalidateSpy).toHaveBeenCalledWith({
        queryKey: ["/api/v1/dashboard/metrics"],
      });
    });
  });

  it("invalidates React Query cache when risks Realtime event received", async () => {
    const invalidateSpy = jest.spyOn(queryClient, "invalidateQueries");

    renderDashboard();

    await waitFor(() => {
      expect(capturedEventHandlers.has("risks")).toBe(true);
    });

    const mockPayload = {
      table: "risks",
      eventType: "UPDATE",
      new: { id: 2, status: "high" },
      old: { id: 2, status: "medium" },
    };

    const risksHandler = capturedEventHandlers.get("risks");
    risksHandler(mockPayload);

    await waitFor(() => {
      expect(invalidateSpy).toHaveBeenCalled();
    });
  });

  it("invalidates React Query cache when business_processes Realtime event received", async () => {
    const invalidateSpy = jest.spyOn(queryClient, "invalidateQueries");

    renderDashboard();

    await waitFor(() => {
      expect(capturedEventHandlers.has("business_processes")).toBe(true);
    });

    const mockPayload = {
      table: "business_processes",
      eventType: "DELETE",
      new: {},
      old: { id: 3, name: "Deleted Process" },
    };

    const processesHandler = capturedEventHandlers.get("business_processes");
    processesHandler(mockPayload);

    await waitFor(() => {
      expect(invalidateSpy).toHaveBeenCalled();
    });
  });

  it("activates fallback polling when Realtime status is disconnected", async () => {
    // Mock subscription failure
    mockChannel.subscribe = jest.fn().mockImplementation((callback) => {
      setTimeout(() => callback("CHANNEL_ERROR"), 0);
      return mockChannel;
    });

    renderDashboard();

    // Wait for status to update to disconnected
    await waitFor(
      () => {
        expect(screen.getByText("Disconnected")).toBeInTheDocument();
      },
      { timeout: 2000 }
    );

    // Verify fallback polling indicator is shown
    expect(screen.getByText(/Fallback polling is currently ACTIVE/i)).toBeInTheDocument();
  });

  it("disables polling when Realtime reconnects successfully", async () => {
    let subscribeCallback: ((status: string) => void) | null = null;

    // Mock subscription with delayed success
    mockChannel.subscribe = jest.fn().mockImplementation((callback) => {
      subscribeCallback = callback;
      // Initially fail
      setTimeout(() => callback("CHANNEL_ERROR"), 0);
      return mockChannel;
    });

    renderDashboard();

    // Wait for disconnected state
    await waitFor(() => {
      expect(screen.getByText("Disconnected")).toBeInTheDocument();
    });

    // Simulate reconnection
    if (subscribeCallback) {
      subscribeCallback("SUBSCRIBED");
    }

    // Wait for connected state
    await waitFor(() => {
      expect(screen.getByText("Connected")).toBeInTheDocument();
    });

    // Fallback polling warning should not be shown
    expect(screen.queryByText(/Fallback polling is currently ACTIVE/i)).not.toBeInTheDocument();
  });

  it("displays connection status indicator in header", async () => {
    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText(/Connected|Connecting|Disconnected/i)).toBeInTheDocument();
    });
  });

  it("filters Realtime subscriptions by tenant_id", async () => {
    renderDashboard();

    await waitFor(() => {
      expect(mockChannel.on).toHaveBeenCalledWith(
        "postgres_changes",
        expect.objectContaining({
          filter: expect.stringContaining("tenant_id=eq."),
        }),
        expect.any(Function)
      );
    });
  });

  it("cleans up all subscriptions on unmount", async () => {
    const { unmount } = renderDashboard();

    await waitFor(() => {
      expect(mockChannel.subscribe).toHaveBeenCalledTimes(3);
    });

    unmount();

    // Should remove all 3 channels
    await waitFor(() => {
      expect(mockSupabase.removeChannel).toHaveBeenCalledTimes(3);
    });
  });
});
