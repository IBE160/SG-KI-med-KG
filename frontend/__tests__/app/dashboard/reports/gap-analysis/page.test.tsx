import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import GapAnalysisPage from "@/app/dashboard/reports/gap-analysis/page";

// Mock hooks
jest.mock("@/hooks/useMappings", () => ({
  useRegulatoryFrameworks: jest.fn(),
}));

jest.mock("@/hooks/useGapAnalysis", () => ({
  useGapAnalysisReport: jest.fn(),
}));

jest.mock("@/lib/role", () => ({
  RoleGuard: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

// Mock UI components
jest.mock("@/components/ui/select", () => ({
  Select: ({ value, onValueChange, children }: any) => (
    <div data-testid="select">
      <button onClick={() => onValueChange("fw1")} data-testid="select-trigger">
        {value ? "Selected" : "Select..."}
      </button>
      {children}
    </div>
  ),
  SelectTrigger: ({ children }: any) => <div>{children}</div>,
  SelectValue: () => <div>Value</div>,
  SelectContent: ({ children }: any) => <div>{children}</div>,
  SelectItem: ({ value, children }: any) => <div data-value={value}>{children}</div>,
}));

// Import mocked hooks
const { useRegulatoryFrameworks } = require("@/hooks/useMappings");
const { useGapAnalysisReport } = require("@/hooks/useGapAnalysis");

describe("GapAnalysisPage", () => {
  const originalPrint = window.print;

  beforeEach(() => {
    jest.clearAllMocks();
    window.print = jest.fn();

    // Default mocks
    useRegulatoryFrameworks.mockReturnValue({
      data: [{ id: "fw1", name: "Framework 1" }],
      isLoading: false,
    });

    useGapAnalysisReport.mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
    });
  });

  afterAll(() => {
    window.print = originalPrint;
  });

  it("renders correctly", () => {
    render(<GapAnalysisPage />);
    expect(screen.getByText("Gap Analysis Report")).toBeInTheDocument();
    expect(screen.getByText("Select Framework")).toBeInTheDocument();
  });

  it("triggers report fetching on selection", () => {
    useGapAnalysisReport.mockReturnValue({
      data: {
        framework_id: "fw1",
        framework_name: "Framework 1",
        total_requirements: 10,
        mapped_requirements: 8,
        unmapped_requirements: 2,
        coverage_percentage: 80.0,
        gaps: [
          { requirement_id: "r1", requirement_name: "Req 1", requirement_description: "Desc 1" }
        ]
      },
      isLoading: false,
    });

    render(<GapAnalysisPage />);
    
    // Simulate selection
    fireEvent.click(screen.getByTestId("select-trigger"));
    
    expect(screen.getByText("Total Requirements")).toBeInTheDocument();
    expect(screen.getByText("80.0%")).toBeInTheDocument();
    expect(screen.getByText("Req 1")).toBeInTheDocument();
  });

  it("shows loading state", () => {
    // Select an ID to trigger loading state rendering
    // But we need to mock useState... can't easily.
    // Instead, rely on the fact that if useGapAnalysisReport returns isLoading=true,
    // the loading skeleton should appear IF selectedId is set.
    // Since we control the mock Select, clicking it sets the state.
    
    useGapAnalysisReport.mockReturnValue({
      data: null,
      isLoading: true,
    });

    render(<GapAnalysisPage />);
    fireEvent.click(screen.getByTestId("select-trigger"));
    
    // Check for skeleton class logic or structure?
    // The skeleton has className "h-32 w-full".
    // Better to check that report content is NOT there yet.
    expect(screen.queryByText("Total Requirements")).not.toBeInTheDocument();
  });

  it("handles print button", () => {
    useGapAnalysisReport.mockReturnValue({
      data: {
        framework_id: "fw1",
        framework_name: "Framework 1",
        total_requirements: 10,
        mapped_requirements: 8,
        unmapped_requirements: 2,
        coverage_percentage: 80.0,
        gaps: []
      },
      isLoading: false,
    });

    render(<GapAnalysisPage />);
    fireEvent.click(screen.getByTestId("select-trigger"));
    
    const printBtn = screen.getByText("Print Report");
    fireEvent.click(printBtn);
    expect(window.print).toHaveBeenCalled();
  });
});
