import { render, screen } from "@testing-library/react";
import { RealtimeStatusIndicator } from "@/components/custom/RealtimeStatusIndicator";
import userEvent from "@testing-library/user-event";

describe("RealtimeStatusIndicator Component", () => {
  it("displays green badge when status is 'connected'", () => {
    render(<RealtimeStatusIndicator status="connected" />);

    const badge = screen.getByText("Connected");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("bg-green-500");
  });

  it("displays yellow badge when status is 'connecting'", () => {
    render(<RealtimeStatusIndicator status="connecting" />);

    const badge = screen.getByText("Connecting");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("bg-yellow-500");
  });

  it("displays red badge when status is 'disconnected'", () => {
    render(<RealtimeStatusIndicator status="disconnected" />);

    const badge = screen.getByText("Disconnected");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("bg-red-500");
  });

  it("shows correct tooltip for 'connected' status", async () => {
    const user = userEvent.setup();
    render(<RealtimeStatusIndicator status="connected" />);

    const badge = screen.getByText("Connected");
    await user.hover(badge);

    // Wait for tooltip to appear (use getAllByText since Radix renders multiple for accessibility)
    const tooltips = await screen.findAllByText("Real-time updates active");
    expect(tooltips.length).toBeGreaterThan(0);
  });

  it("shows correct tooltip for 'connecting' status", async () => {
    const user = userEvent.setup();
    render(<RealtimeStatusIndicator status="connecting" />);

    const badge = screen.getByText("Connecting");
    await user.hover(badge);

    const tooltips = await screen.findAllByText("Establishing connection...");
    expect(tooltips.length).toBeGreaterThan(0);
  });

  it("shows correct tooltip for 'disconnected' status", async () => {
    const user = userEvent.setup();
    render(<RealtimeStatusIndicator status="disconnected" />);

    const badge = screen.getByText("Disconnected");
    await user.hover(badge);

    const tooltips = await screen.findAllByText("Using fallback polling (60s)");
    expect(tooltips.length).toBeGreaterThan(0);
  });

  it("renders status indicator dot", () => {
    const { container } = render(<RealtimeStatusIndicator status="connected" />);

    const badge = screen.getByText(/Connected/i);
    expect(badge.textContent).toContain("●");
  });

  it("applies cursor-help class for tooltip affordance", () => {
    render(<RealtimeStatusIndicator status="connected" />);

    const badge = screen.getByText("Connected");
    expect(badge).toHaveClass("cursor-help");
  });

  it("updates display when status prop changes", () => {
    const { rerender } = render(<RealtimeStatusIndicator status="connecting" />);

    expect(screen.getByText("Connecting")).toBeInTheDocument();

    rerender(<RealtimeStatusIndicator status="connected" />);

    expect(screen.queryByText("Connecting")).not.toBeInTheDocument();
    expect(screen.getByText("Connected")).toBeInTheDocument();
  });

  it("applies correct color transition classes", () => {
    render(<RealtimeStatusIndicator status="connected" />);

    const badge = screen.getByText("Connected");
    expect(badge).toHaveClass("bg-green-500", "hover:bg-green-600");
  });
});
