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
          const apiUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/v1/users/me`;
          console.log("Fetching user role from:", apiUrl);

          const response = await fetch(apiUrl, {
            headers: {
              Authorization: `Bearer ${session.access_token}`,
            },
          });

          console.log("Role fetch response status:", response.status);

          if (response.ok) {
            const userData = await response.json();
            console.log("User data from backend:", userData);
            setRole(userData.role || "general_user");
          } else {
            const errorText = await response.text();
            console.error("Failed to fetch from backend:", response.status, errorText);
            // Fallback to JWT if backend fetch fails
            const decoded: any = jwtDecode(session.access_token);
            const appRole = decoded.app_metadata?.role;
            console.log("Falling back to JWT role:", appRole);
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
          const apiUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/v1/users/me`;
          const response = await fetch(apiUrl, {
            headers: {
              Authorization: `Bearer ${session.access_token}`,
            },
          });
          if (response.ok) {
            const userData = await response.json();
            console.log("Auth state change - User data:", userData);
            setRole(userData.role || "general_user");
          } else {
            console.log("Auth state change - Backend fetch failed, using JWT");
            const decoded: any = jwtDecode(session.access_token);
            setRole(decoded.app_metadata?.role || "general_user");
          }
        } catch (e) {
          console.error("Auth state change error:", e);
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
