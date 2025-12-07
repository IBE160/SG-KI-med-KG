import { renderHook, waitFor } from "@testing-library/react";

// Use manual mock for @/lib/supabase
jest.mock("@/lib/supabase");

// Import hook and mocked supabase
import { useRealtimeSubscription } from "@/hooks/useRealtimeSubscription";
import * as SupabaseLib from "@/lib/supabase";

const createClient = jest.mocked(SupabaseLib.createClient);

describe("useRealtimeSubscription Hook", () => {
  let mockChannel: any;
  let mockSupabase: any;
  let mockSubscribe: jest.Mock;
  let mockOn: jest.Mock;
  let mockRemoveChannel: jest.Mock;

  beforeEach(() => {
    mockSubscribe = jest.fn();
    mockOn = jest.fn();
    mockRemoveChannel = jest.fn();

    mockChannel = {
      on: mockOn,
      subscribe: mockSubscribe,
    };

    mockSupabase = {
      channel: jest.fn().mockReturnValue(mockChannel),
      removeChannel: mockRemoveChannel,
    };

    createClient.mockReturnValue(mockSupabase as any);

    // Setup default chaining behavior
    mockOn.mockReturnValue(mockChannel);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("establishes Supabase Realtime channel subscription", () => {
    const onEvent = jest.fn();
    const tableName = "controls";
    const filterCriteria = { tenant_id: "tenant-123" };

    renderHook(() =>
      useRealtimeSubscription({
        tableName,
        filterCriteria,
        onEvent,
        enabled: true,
      })
    );

    expect(mockSupabase.channel).toHaveBeenCalledWith(
      `realtime:${tableName}:${filterCriteria.tenant_id}`
    );
    expect(mockOn).toHaveBeenCalledWith(
      "postgres_changes",
      {
        event: "*",
        schema: "public",
        table: tableName,
        filter: `tenant_id=eq.${filterCriteria.tenant_id}`,
      },
      expect.any(Function)
    );
    expect(mockSubscribe).toHaveBeenCalled();
  });

  it("returns status 'connecting' initially", () => {
    const onEvent = jest.fn();

    const { result } = renderHook(() =>
      useRealtimeSubscription({
        tableName: "risks",
        filterCriteria: { tenant_id: "tenant-456" },
        onEvent,
      })
    );

    expect(result.current.status).toBe("connecting");
  });

  it("returns status 'connected' when subscription succeeds", async () => {
    const onEvent = jest.fn();

    mockSubscribe.mockImplementation((callback: (status: string) => void) => {
      // Simulate successful subscription
      setTimeout(() => callback("SUBSCRIBED"), 0);
      return mockChannel;
    });

    const { result } = renderHook(() =>
      useRealtimeSubscription({
        tableName: "business_processes",
        filterCriteria: { tenant_id: "tenant-789" },
        onEvent,
      })
    );

    await waitFor(() => {
      expect(result.current.status).toBe("connected");
    });
  });

  it("returns status 'disconnected' when subscription fails", async () => {
    const onEvent = jest.fn();

    mockSubscribe.mockImplementation((callback: (status: string) => void) => {
      setTimeout(() => callback("CHANNEL_ERROR"), 0);
      return mockChannel;
    });

    const { result } = renderHook(() =>
      useRealtimeSubscription({
        tableName: "controls",
        filterCriteria: { tenant_id: "tenant-err" },
        onEvent,
      })
    );

    await waitFor(() => {
      expect(result.current.status).toBe("disconnected");
    });
  });

  it("calls onEvent callback when INSERT event received", async () => {
    const onEvent = jest.fn();
    let capturedEventHandler: any;

    mockOn.mockImplementation((eventType: string, config: any, handler: any) => {
      capturedEventHandler = handler;
      return mockChannel;
    });

    renderHook(() =>
      useRealtimeSubscription({
        tableName: "controls",
        filterCriteria: { tenant_id: "tenant-insert" },
        onEvent,
      })
    );

    // Simulate INSERT event from Supabase
    const mockPayload = {
      table: "controls",
      eventType: "INSERT",
      new: { id: 1, name: "New Control", tenant_id: "tenant-insert" },
      old: {},
    };

    capturedEventHandler(mockPayload);

    await waitFor(() => {
      expect(onEvent).toHaveBeenCalledWith({
        table: "controls",
        eventType: "INSERT",
        new: mockPayload.new,
        old: {},
      });
    });
  });

  it("calls onEvent callback when UPDATE event received", async () => {
    const onEvent = jest.fn();
    let capturedEventHandler: any;

    mockOn.mockImplementation((eventType: string, config: any, handler: any) => {
      capturedEventHandler = handler;
      return mockChannel;
    });

    renderHook(() =>
      useRealtimeSubscription({
        tableName: "risks",
        filterCriteria: { tenant_id: "tenant-update" },
        onEvent,
      })
    );

    const mockPayload = {
      table: "risks",
      eventType: "UPDATE",
      new: { id: 2, status: "active" },
      old: { id: 2, status: "pending" },
    };

    capturedEventHandler(mockPayload);

    await waitFor(() => {
      expect(onEvent).toHaveBeenCalledWith({
        table: "risks",
        eventType: "UPDATE",
        new: mockPayload.new,
        old: mockPayload.old,
      });
    });
  });

  it("calls onEvent callback when DELETE event received", async () => {
    const onEvent = jest.fn();
    let capturedEventHandler: any;

    mockOn.mockImplementation((eventType: string, config: any, handler: any) => {
      capturedEventHandler = handler;
      return mockChannel;
    });

    renderHook(() =>
      useRealtimeSubscription({
        tableName: "business_processes",
        filterCriteria: { tenant_id: "tenant-delete" },
        onEvent,
      })
    );

    const mockPayload = {
      table: "business_processes",
      eventType: "DELETE",
      new: {},
      old: { id: 3, name: "Deleted Process" },
    };

    capturedEventHandler(mockPayload);

    await waitFor(() => {
      expect(onEvent).toHaveBeenCalledWith({
        table: "business_processes",
        eventType: "DELETE",
        new: {},
        old: mockPayload.old,
      });
    });
  });

  it("cleans up subscription on unmount", () => {
    const onEvent = jest.fn();

    const { unmount } = renderHook(() =>
      useRealtimeSubscription({
        tableName: "controls",
        filterCriteria: { tenant_id: "tenant-cleanup" },
        onEvent,
      })
    );

    unmount();

    expect(mockRemoveChannel).toHaveBeenCalledWith(mockChannel);
  });

  it("does not subscribe when enabled is false", () => {
    const onEvent = jest.fn();

    const { result } = renderHook(() =>
      useRealtimeSubscription({
        tableName: "controls",
        filterCriteria: { tenant_id: "tenant-disabled" },
        onEvent,
        enabled: false,
      })
    );

    expect(mockSupabase.channel).not.toHaveBeenCalled();
    expect(result.current.status).toBe("disconnected");
  });

  it("filters events by tenant_id", () => {
    const onEvent = jest.fn();
    const tenantId = "specific-tenant-123";

    renderHook(() =>
      useRealtimeSubscription({
        tableName: "controls",
        filterCriteria: { tenant_id: tenantId },
        onEvent,
      })
    );

    expect(mockOn).toHaveBeenCalledWith(
      "postgres_changes",
      expect.objectContaining({
        filter: `tenant_id=eq.${tenantId}`,
      }),
      expect.any(Function)
    );
  });

  it("creates unique channel name per table and tenant", () => {
    const onEvent = jest.fn();

    renderHook(() =>
      useRealtimeSubscription({
        tableName: "risks",
        filterCriteria: { tenant_id: "unique-tenant" },
        onEvent,
      })
    );

    expect(mockSupabase.channel).toHaveBeenCalledWith("realtime:risks:unique-tenant");
  });
});
