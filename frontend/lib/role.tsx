"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { createClient } from "@/lib/supabase";
import { jwtDecode } from "jwt-decode";

export function useRole() {
  const [role, setRole] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const supabase = createClient();

  useEffect(() => {
    const getUserRole = async () => {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (session?.access_token) {
        try {
          // Fetch role from backend API for authoritative source
          const response = await fetch("/api/v1/users/me", {
            headers: {
              Authorization: `Bearer ${session.access_token}`,
            },
          });

          if (response.ok) {
            const userData = await response.json();
            setRole(userData.role || "general_user");
          } else {
            // Fallback to JWT if backend fetch fails
            const decoded: any = jwtDecode(session.access_token);
            const appRole = decoded.app_metadata?.role;
            setRole(appRole || "general_user");
          }
        } catch (e) {
          console.error("Failed to get user role", e);
          setRole("general_user");
        }
      }
      setLoading(false);
    };

    getUserRole();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      if (session?.access_token) {
        try {
          // Fetch updated role from backend
          const response = await fetch("/api/v1/users/me", {
            headers: {
              Authorization: `Bearer ${session.access_token}`,
            },
          });
          if (response.ok) {
            const userData = await response.json();
            setRole(userData.role || "general_user");
          } else {
            const decoded: any = jwtDecode(session.access_token);
            setRole(decoded.app_metadata?.role || "general_user");
          }
        } catch (e) {
          const decoded: any = jwtDecode(session.access_token);
          setRole(decoded.app_metadata?.role || "general_user");
        }
      } else {
        setRole(null);
      }
    });

    return () => subscription.unsubscribe();
  }, [supabase.auth]);

  return { role, loading, isAdmin: role === "admin" };
}

export function RoleGuard({
  children,
  allowedRoles,
}: {
  children: React.ReactNode;
  allowedRoles: string[];
}) {
  const { role, loading } = useRole();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading) {
      if (!role || !allowedRoles.includes(role)) {
        // Redirect to dashboard if authorized but wrong role, or login if not auth
        if (role) {
          router.push("/dashboard");
        } else {
          router.push("/login");
        }
      }
    }
  }, [role, loading, router, allowedRoles]);

  if (loading) return <div className="p-4">Checking permissions...</div>; // Or a spinner

  if (!role || !allowedRoles.includes(role)) {
    return null; // Will redirect in useEffect
  }

  return <>{children}</>;
}
