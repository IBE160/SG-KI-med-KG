import { render, screen, fireEvent } from "@testing-library/react";
import BPOPendingReviewsPage from "@/app/(dashboard)/bpo/reviews/page";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";

// Mock hooks
jest.mock("@tanstack/react-query", () => ({
  useQuery: jest.fn(),
  useQueryClient: jest.fn(() => ({
    invalidateQueries: jest.fn(),
  })),
}));

jest.mock("next/navigation", () => ({
  useRouter: jest.fn(),
}));

// Mock API client if needed (not needed if mocking useQuery return)
jest.mock("../../../../../app/clientService", () => ({
  assessmentsGetPendingReviews: jest.fn(),
}));

describe("BPOPendingReviewsPage", () => {
  const mockPush = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });
  });

  it("renders loading state", () => {
    (useQuery as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    });

    const { container } = render(<BPOPendingReviewsPage />);
    // Check for skeletons
    const skeletons = container.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders error state", () => {
    (useQuery as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error("Failed to fetch"),
    });

    render(<BPOPendingReviewsPage />);
    expect(screen.getByText("Failed to fetch")).toBeInTheDocument();
  });

  it("renders empty state", () => {
    (useQuery as jest.Mock).mockReturnValue({
      data: { items: [], total: 0, page: 1, size: 20 },
      isLoading: false,
      error: null,
    });

    render(<BPOPendingReviewsPage />);
    expect(screen.getByText("No pending reviews. All caught up!")).toBeInTheDocument();
  });

  it("renders list of reviews", () => {
    const mockItems = [
      {
        suggestion_id: 1,
        business_process_name: "BP 1",
        risk_name: "Risk 1",
        control_name: "Control 1",
        source_reference: "Ref 1",
        created_at: "2023-01-01T00:00:00Z",
      },
    ];

    (useQuery as jest.Mock).mockReturnValue({
      data: { items: mockItems, total: 1, page: 1, size: 20 },
      isLoading: false,
      error: null,
    });

    render(<BPOPendingReviewsPage />);
    expect(screen.getByText("BP 1")).toBeInTheDocument();
    expect(screen.getByText("Risk 1")).toBeInTheDocument();
    expect(screen.getByText("Control 1")).toBeInTheDocument();
  });

  it("navigates to detail page on row click", () => {
    const mockItems = [
      {
        suggestion_id: 1,
        business_process_name: "BP 1",
        risk_name: "Risk 1",
        control_name: "Control 1",
        source_reference: "Ref 1",
        created_at: "2023-01-01T00:00:00Z",
      },
    ];

    (useQuery as jest.Mock).mockReturnValue({
      data: { items: mockItems, total: 1, page: 1, size: 20 },
      isLoading: false,
      error: null,
    });

    render(<BPOPendingReviewsPage />);
    
    // Find the row (using text from the row)
    const rowCell = screen.getByText("BP 1");
    fireEvent.click(rowCell);

    expect(mockPush).toHaveBeenCalledWith("/dashboard/bpo/reviews/1");
  });
});
