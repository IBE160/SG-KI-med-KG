"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Home,
  List,
  ShieldCheck,
  AlertTriangle,
  GitBranch,
  Scale,
  UserCog,
  FileText,
  ClipboardCheck,
} from "lucide-react";
import Image from "next/image";

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { logout } from "@/lib/logout";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useRole } from "@/lib/role";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { role, fullName, email, isAdmin } = useRole();
  const router = useRouter();

  const isComplianceOfficer = role === "compliance_officer";

  const getInitials = (name: string | null, emailAddress: string | null) => {
    if (!name) {
      // Fallback to email initial if no name
      if (emailAddress && emailAddress.length > 0) {
        return emailAddress.charAt(0).toUpperCase();
      }
      return "U";
    }
    const parts = name.trim().split(" ");
    if (parts.length === 0) {
      // If name is empty after trimming, fallback to email
      if (emailAddress && emailAddress.length > 0) {
        return emailAddress.charAt(0).toUpperCase();
      }
      return "U";
    }
    if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
    return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
  };

  const handleLogout = async () => {
    try {
      await logout();
      router.push("/login");
    } catch (error) {
      console.error("Logout error:", error);
      // Force redirect anyway
      router.push("/login");
    }
  };

  return (
    <div className="flex min-h-screen">
      <aside className="fixed inset-y-0 left-0 z-10 w-16 flex flex-col border-r bg-background p-4">
        {/* ... (aside content remains same) ... */}
        <div className="flex flex-col items-center gap-4">
          <Link
            href="/"
            className="flex items-center justify-center rounded-full mb-4"
          >
            <Image
              src="/images/vinta.png"
              alt="Vinta"
              width={48}
              height={48}
              className="object-cover transition-transform duration-200 hover:scale-105"
            />
          </Link>

          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Link
                  href="/dashboard"
                  className="flex items-center justify-center w-10 h-10 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted"
                >
                  <List className="h-5 w-5" />
                </Link>
              </TooltipTrigger>
              <TooltipContent side="right">Dashboard</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Link
                  href="/dashboard/controls"
                  className="flex items-center justify-center w-10 h-10 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted"
                >
                  <ShieldCheck className="h-5 w-5" />
                </Link>
              </TooltipTrigger>
              <TooltipContent side="right">Controls</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Link
                  href="/dashboard/risks"
                  className="flex items-center justify-center w-10 h-10 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted"
                >
                  <AlertTriangle className="h-5 w-5" />
                </Link>
              </TooltipTrigger>
              <TooltipContent side="right">Risks</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Link
                  href="/dashboard/business-processes"
                  className="flex items-center justify-center w-10 h-10 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted"
                >
                  <GitBranch className="h-5 w-5" />
                </Link>
              </TooltipTrigger>
              <TooltipContent side="right">Business Processes</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Link
                  href="/dashboard/regulatory-frameworks"
                  className="flex items-center justify-center w-10 h-10 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted"
                >
                  <Scale className="h-5 w-5" />
                </Link>
              </TooltipTrigger>
              <TooltipContent side="right">
                Regulatory Frameworks
              </TooltipContent>
            </Tooltip>

            {(isAdmin || isComplianceOfficer) && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Link
                    href="/dashboard/compliance/review"
                    className="flex items-center justify-center w-10 h-10 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted"
                  >
                    <ClipboardCheck className="h-5 w-5" />
                  </Link>
                </TooltipTrigger>
                <TooltipContent side="right">AI Review</TooltipContent>
              </Tooltip>
            )}

            {isAdmin && (
              <>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Link
                      href="/dashboard/admin/documents"
                      className="flex items-center justify-center w-10 h-10 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted"
                    >
                      <FileText className="h-5 w-5" />
                    </Link>
                  </TooltipTrigger>
                  <TooltipContent side="right">Documents</TooltipContent>
                </Tooltip>

                <Tooltip>
                  <TooltipTrigger asChild>
                    <Link
                      href="/dashboard/admin/users"
                      className="flex items-center justify-center w-10 h-10 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted"
                    >
                      <UserCog className="h-5 w-5" />
                    </Link>
                  </TooltipTrigger>
                  <TooltipContent side="right">User Management</TooltipContent>
                </Tooltip>
              </>
            )}
          </TooltipProvider>
        </div>
      </aside>
      <main className="ml-16 w-full p-8 bg-muted/40">
        <header className="flex justify-between items-center mb-6">
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink asChild>
                  <Link href="/" className="flex items-center gap-2">
                    <Home className="h-4 w-4" />
                    <span>Home</span>
                  </Link>
                </BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator>/</BreadcrumbSeparator>
              <BreadcrumbItem>
                <BreadcrumbLink asChild>
                  <Link href="/dashboard" className="flex items-center gap-2">
                    <List className="h-4 w-4" />
                    <span>Dashboard</span>
                  </Link>
                </BreadcrumbLink>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
          <div className="relative">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center justify-center w-10 h-10 rounded-full bg-gray-300 hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                  <Avatar>
                    <AvatarFallback>{getInitials(fullName, email)}</AvatarFallback>
                  </Avatar>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" side="bottom" className="w-56">
                <div className="px-4 py-2 text-sm border-b">
                  <div className="font-semibold text-lg">{fullName || "User"}</div>
                  <div className="text-muted-foreground text-xs capitalize">
                    {role ? role.replace("_", " ") : "Loading..."}
                  </div>
                </div>
                <DropdownMenuItem asChild>
                  <Link href="/support" className="cursor-pointer">
                    Support
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={handleLogout}
                  className="cursor-pointer text-red-600 focus:text-red-600"
                >
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>
        <section className="grid gap-6">{children}</section>
      </main>
    </div>
  );
}
