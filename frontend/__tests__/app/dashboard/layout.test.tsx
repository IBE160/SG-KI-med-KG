import React from 'react';
import { render, screen } from '@testing-library/react';
import DashboardLayout from '@/app/dashboard/layout'; // Adjust import if needed based on alias
import { useRole } from '@/lib/role';

// Mock the useRole hook
jest.mock('@/lib/role', () => ({
  useRole: jest.fn(),
}));

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// Mock Image component (Next.js Image)
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: any) => <img {...props} />,
}));

describe('DashboardLayout', () => {
  it('displays initials from full name', () => {
    (useRole as jest.Mock).mockReturnValue({
      role: 'general_user',
      fullName: 'John Doe',
      email: 'john@example.com',
      loading: false,
      isAdmin: false,
    });

    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    // Check for initials in AvatarFallback.
    // Radix Avatar Fallback renders text.
    expect(screen.getByText('JD')).toBeInTheDocument();

    // Check for Full Name in tooltip/dropdown content
    // Note: Dropdown content is usually hidden until triggered, but we can check if it exists in DOM or trigger it.
    // For simplicity, let's just check if the Avatar Fallback rendered correctly for now.
  });

  it('displays single initial for single name', () => {
    (useRole as jest.Mock).mockReturnValue({
      role: 'general_user',
      fullName: 'Admin',
      email: 'admin@example.com',
      loading: false,
      isAdmin: false,
    });

    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    expect(screen.getByText('A')).toBeInTheDocument();
  });

  it('displays email initial when no name is set', () => {
    (useRole as jest.Mock).mockReturnValue({
      role: 'general_user',
      fullName: null,
      email: 'john@example.com',
      loading: false,
      isAdmin: false,
    });

    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    expect(screen.getByText('J')).toBeInTheDocument();
  });

  it('displays fallback U when no name and no email', () => {
    (useRole as jest.Mock).mockReturnValue({
      role: 'general_user',
      fullName: null,
      email: null,
      loading: false,
      isAdmin: false,
    });

    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    expect(screen.getByText('U')).toBeInTheDocument();
  });
});
