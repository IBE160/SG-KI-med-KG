import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { DualListSelector, DualListItem } from "@/components/custom/DualListSelector";

describe("DualListSelector Component", () => {
  const mockAvailableItems: DualListItem[] = [
    { id: "1", name: "Item 1" },
    { id: "2", name: "Item 2" },
    { id: "3", name: "Item 3" },
  ];

  const mockSelectedItems: DualListItem[] = [
    { id: "4", name: "Item 4" },
    { id: "5", name: "Item 5" },
  ];

  const mockOnSelectionChange = jest.fn();

  beforeEach(() => {
    mockOnSelectionChange.mockClear();
  });

  it("renders available and selected lists", () => {
    render(
      <DualListSelector
        availableItems={mockAvailableItems}
        selectedItems={mockSelectedItems}
        onSelectionChange={mockOnSelectionChange}
      />
    );

    expect(screen.getByText("Available Items")).toBeInTheDocument();
    expect(screen.getByText("Selected Items")).toBeInTheDocument();
  });

  it("displays all available items", () => {
    render(
      <DualListSelector
        availableItems={mockAvailableItems}
        selectedItems={mockSelectedItems}
        onSelectionChange={mockOnSelectionChange}
      />
    );

    mockAvailableItems.forEach((item) => {
      expect(screen.getByText(item.name)).toBeInTheDocument();
    });
  });

  it("displays all selected items", () => {
    render(
      <DualListSelector
        availableItems={mockAvailableItems}
        selectedItems={mockSelectedItems}
        onSelectionChange={mockOnSelectionChange}
      />
    );

    mockSelectedItems.forEach((item) => {
      expect(screen.getByText(item.name)).toBeInTheDocument();
    });
  });

  it("allows selecting items by clicking checkbox", async () => {
    const user = userEvent.setup();
    render(
      <DualListSelector
        availableItems={mockAvailableItems}
        selectedItems={mockSelectedItems}
        onSelectionChange={mockOnSelectionChange}
      />
    );

    const checkboxes = screen.getAllByRole("checkbox");
    const firstAvailableCheckbox = checkboxes[0];

    await user.click(firstAvailableCheckbox);
    expect(firstAvailableCheckbox).toBeChecked();
  });

  it("filters items based on search input", async () => {
    const user = userEvent.setup();
    render(
      <DualListSelector
        availableItems={mockAvailableItems}
        selectedItems={mockSelectedItems}
        onSelectionChange={mockOnSelectionChange}
      />
    );

    const searchInputs = screen.getAllByPlaceholderText("Search...");
    const availableSearch = searchInputs[0];

    await user.type(availableSearch, "Item 1");

    expect(screen.getByText("Item 1")).toBeInTheDocument();
    expect(screen.queryByText("Item 2")).not.toBeInTheDocument();
    expect(screen.queryByText("Item 3")).not.toBeInTheDocument();
  });

  it("displays item counts correctly", () => {
    render(
      <DualListSelector
        availableItems={mockAvailableItems}
        selectedItems={mockSelectedItems}
        onSelectionChange={mockOnSelectionChange}
      />
    );

    expect(screen.getByText("3 items")).toBeInTheDocument();
    expect(screen.getByText("2 items")).toBeInTheDocument();
  });

  it("shows empty state when no items available", () => {
    render(
      <DualListSelector
        availableItems={[]}
        selectedItems={mockSelectedItems}
        onSelectionChange={mockOnSelectionChange}
      />
    );

    expect(screen.getByText("No items available")).toBeInTheDocument();
  });

  it("shows empty state when no items selected", () => {
    render(
      <DualListSelector
        availableItems={mockAvailableItems}
        selectedItems={[]}
        onSelectionChange={mockOnSelectionChange}
      />
    );

    expect(screen.getByText("No items selected")).toBeInTheDocument();
  });

  it("uses custom titles when provided", () => {
    render(
      <DualListSelector
        availableItems={mockAvailableItems}
        selectedItems={mockSelectedItems}
        onSelectionChange={mockOnSelectionChange}
        availableTitle="Custom Available"
        selectedTitle="Custom Selected"
      />
    );

    expect(screen.getByText("Custom Available")).toBeInTheDocument();
    expect(screen.getByText("Custom Selected")).toBeInTheDocument();
  });

  it("supports keyboard navigation with Space key", async () => {
    const user = userEvent.setup();
    render(
      <DualListSelector
        availableItems={mockAvailableItems}
        selectedItems={mockSelectedItems}
        onSelectionChange={mockOnSelectionChange}
      />
    );

    const firstItem = screen.getByText("Item 1").closest("[role=button]");
    if (firstItem) {
      firstItem.focus();
      await user.keyboard(" ");

      const checkboxes = screen.getAllByRole("checkbox");
      expect(checkboxes[0]).toBeChecked();
    }
  });

  it("supports keyboard navigation with Enter key", async () => {
    const user = userEvent.setup();
    render(
      <DualListSelector
        availableItems={mockAvailableItems}
        selectedItems={mockSelectedItems}
        onSelectionChange={mockOnSelectionChange}
      />
    );

    const firstItem = screen.getByText("Item 1").closest("[role=button]");
    if (firstItem) {
      firstItem.focus();
      await user.keyboard("{Enter}");

      const checkboxes = screen.getAllByRole("checkbox");
      expect(checkboxes[0]).toBeChecked();
    }
  });

  it("applies correct styling to selected items", async () => {
    const user = userEvent.setup();
    render(
      <DualListSelector
        availableItems={mockAvailableItems}
        selectedItems={mockSelectedItems}
        onSelectionChange={mockOnSelectionChange}
      />
    );

    const firstItem = screen.getByText("Item 1").closest("div");
    if (firstItem?.parentElement) {
      await user.click(firstItem.parentElement);
      expect(firstItem.parentElement).toHaveClass("bg-accent");
    }
  });
});
