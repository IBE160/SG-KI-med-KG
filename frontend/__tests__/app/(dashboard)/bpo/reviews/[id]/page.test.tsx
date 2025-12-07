import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import BPOReviewDetailPage from "@/app/(dashboard)/bpo/reviews/[id]/page";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useRouter, useParams } from "next/navigation";

// Mock hooks
jest.mock("@tanstack/react-query", () => ({
  useQuery: jest.fn(),
  useMutation: jest.fn(),
  useQueryClient: jest.fn(() => ({
    invalidateQueries: jest.fn(),
  })),
}));

jest.mock("next/navigation", () => ({
  useRouter: jest.fn(),
  useParams: jest.fn(),
}));

jest.mock("sonner", () => ({
  toast: {
    success: jest.fn(),
    info: jest.fn(),
    error: jest.fn(),
  },
}));

jest.mock("../../../../../../app/clientService", () => ({
  assessmentsGetSuggestionDetail: jest.fn(),
  assessmentsSubmitAssessment: jest.fn(),
}));

describe("BPOReviewDetailPage", () => {
  const mockPush = jest.fn();
  const mockMutate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });
    (useParams as jest.Mock).mockReturnValue({
      id: "123",
    });
    (useMutation as jest.Mock).mockReturnValue({
      mutate: mockMutate,
      isPending: false,
    });
  });

  it("renders loading state", () => {
    (useQuery as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    });

    const { container } = render(<BPOReviewDetailPage />);
    expect(container.querySelectorAll(".animate-pulse").length).toBeGreaterThan(0);
  });

  it("renders error state", () => {
    (useQuery as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error("Failed to load"),
    });

    render(<BPOReviewDetailPage />);
    expect(screen.getByText("Failed to load")).toBeInTheDocument();
  });

  it("renders suggestion details", () => {
    const mockSuggestion = {
      suggestion_id: "123",
      business_process_name: "Test Process",
      risk_name: "Test Risk",
      risk_description: "Risk Desc",
      control_name: "Test Control",
      control_description: "Control Desc",
      rationale: "AI Rationale Content",
      source_reference: "https://example.com",
      created_at: "2023-01-01T00:00:00Z",
    };

    const mockQueryReturn = {
      data: mockSuggestion,
      isLoading: false,
      error: null,
    };

    (useQuery as jest.Mock).mockReturnValue(mockQueryReturn);

    render(<BPOReviewDetailPage />);

    expect(screen.getByDisplayValue("Test Process")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Risk Desc")).toBeInTheDocument();
    expect(screen.getByText("Test Risk")).toBeInTheDocument();
    expect(screen.getByText("AI Rationale Content")).toBeInTheDocument();
  });

  it("validates residual risk before approval", async () => {
    const mockSuggestion = {
      suggestion_id: "123",
      business_process_name: "Test Process",
      risk_name: "Test Risk",
      risk_description: "Risk Desc",
      control_name: "Test Control",
      control_description: "Control Desc",
      rationale: "AI Rationale",
      source_reference: "https://example.com",
      created_at: "2023-01-01T00:00:00Z",
    };

    const mockQueryReturn = {
      data: mockSuggestion,
      isLoading: false,
      error: null,
    };

    (useQuery as jest.Mock).mockReturnValue(mockQueryReturn);

    render(<BPOReviewDetailPage />);

    const approveButton = screen.getByRole("button", { name: /approve/i });
    fireEvent.click(approveButton);

    // Should show validation error
    await waitFor(() => {
        expect(screen.getByText("Residual risk must be selected before approving")).toBeInTheDocument();
    });
    
    expect(mockMutate).not.toHaveBeenCalled();
  });

  it("enables editing when edit button is clicked", () => {
      const mockSuggestion = {
      suggestion_id: "123",
      business_process_name: "Test Process",
      risk_name: "Test Risk",
      risk_description: "Risk Desc",
      control_name: "Test Control",
      control_description: "Control Desc",
      rationale: "AI Rationale",
      source_reference: "https://example.com",
      created_at: "2023-01-01T00:00:00Z",
    };

    const mockQueryReturn = {
      data: mockSuggestion,
      isLoading: false,
      error: null,
    };

    (useQuery as jest.Mock).mockReturnValue(mockQueryReturn);

    render(<BPOReviewDetailPage />);
    
    const input = screen.getByDisplayValue("Test Process");
    expect(input).toBeDisabled();

    const editButton = screen.getByRole("button", { name: /edit/i });
    fireEvent.click(editButton);

    expect(input).not.toBeDisabled();
  });
});
