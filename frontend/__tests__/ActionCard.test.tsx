import { render, screen } from "@testing-library/react";
import { ActionCard } from "@/components/custom/ActionCard";

// Mock Next.js Link component
jest.mock("next/link", () => {
  const MockLink = ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  );
  MockLink.displayName = "Link";
  return MockLink;
});

describe("ActionCard Component", () => {
  it("renders card with title, metric, and action button", () => {
    render(
      <ActionCard
        title="Pending Reviews"
        metric={5}
        metricLabel="items"
        icon="ClipboardCheck"
        actionLink="/dashboard/bpo/reviews"
      />
    );

    expect(screen.getByText("Pending Reviews")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("items")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /view/i })).toBeInTheDocument();
  });

  it("renders urgent status indicator when status is urgent", () => {
    render(
      <ActionCard
        title="Pending Reviews"
        metric={10}
        metricLabel="items"
        icon="AlertTriangle"
        actionLink="/dashboard/bpo/reviews"
        status="urgent"
      />
    );

    expect(screen.getByText("Requires attention")).toBeInTheDocument();
  });

  it("does not render status indicator when status is null", () => {
    render(
      <ActionCard
        title="My Controls"
        metric={12}
        metricLabel="controls"
        icon="Shield"
        actionLink="/dashboard/controls"
        status={null}
      />
    );

    expect(screen.queryByText("Requires attention")).not.toBeInTheDocument();
  });

  it("renders skeleton loading state when loading prop is true", () => {
    const { container } = render(
      <ActionCard
        title="Loading..."
        metric={0}
        metricLabel=""
        icon="Activity"
        actionLink="#"
        loading={true}
      />
    );

    // Verify skeleton elements are present
    const skeletons = container.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders action link with correct href", () => {
    render(
      <ActionCard
        title="System Health"
        metric={25}
        metricLabel="items"
        icon="Activity"
        actionLink="/dashboard/admin/system"
      />
    );

    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "/dashboard/admin/system");
  });

  it("applies urgent border styling when status is urgent", () => {
    const { container } = render(
      <ActionCard
        title="Overdue Assessments"
        metric={3}
        metricLabel="assessments"
        icon="AlertCircle"
        actionLink="/dashboard/bpo/overdue"
        status="urgent"
      />
    );

    const card = container.querySelector(".border-red-500");
    expect(card).toBeInTheDocument();
  });
});
