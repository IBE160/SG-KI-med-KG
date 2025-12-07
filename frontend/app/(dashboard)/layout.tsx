import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Dashboard - ibe160",
  description: "Real-time risk monitoring dashboard",
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      {/*
        This is a minimal layout for Story 4.2 demo.
        Will be replaced with full dashboard shell (sidebar, header, navigation)
        when Story 4.1 dashboard components are merged.
      */}
      <main>{children}</main>
    </div>
  );
}
