"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { createClient } from "@/lib/supabase";
import { jwtDecode } from "jwt-decode";

export function useRole() {
  const [roles, setRoles] = useState<string[]>([]);
  const [fullName, setFullName] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const supabase = createClient();

  useEffect(() => {
    const getUserRole = async () => {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (session?.access_token) {
        try {
          // Fetch roles from backend API for authoritative source
          // IMPORTANT: Must use absolute URL to avoid Next.js routing to /app/api
          const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
          const apiUrl = `${backendUrl}/api/v1/users/me`;
          console.log("Fetching user roles from:", apiUrl);
          console.log("Backend URL env var:", process.env.NEXT_PUBLIC_API_URL);

          const response = await fetch(apiUrl, {
            headers: {
              Authorization: `Bearer ${session.access_token}`,
            },
            mode: 'cors',
          });

          console.log("Role fetch response status:", response.status);

          if (response.ok) {
            const userData = await response.json();
            console.log("User data from backend:", userData);
            setRoles(userData.roles || ["general_user"]);
            setFullName(userData.full_name || null);
            setEmail(userData.email || null);
          } else {
            const errorText = await response.text();
            console.error("Failed to fetch from backend:", response.status, errorText);
            // Fallback to JWT if backend fetch fails
            const decoded: any = jwtDecode(session.access_token);
            const appRoles = decoded.app_metadata?.roles;
            console.log("Falling back to JWT roles:", appRoles);
            setRoles(appRoles || ["general_user"]);
            setFullName(null);
            setEmail(decoded.email || null);
          }
        } catch (e) {
          console.error("Failed to get user roles", e);
          setRoles(["general_user"]);
          setFullName(null);
          setEmail(null);
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
          // Fetch updated roles from backend
          const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
          const apiUrl = `${backendUrl}/api/v1/users/me`;
          const response = await fetch(apiUrl, {
            headers: {
              Authorization: `Bearer ${session.access_token}`,
            },
            mode: 'cors',
          });
          if (response.ok) {
            const userData = await response.json();
            console.log("Auth state change - User data:", userData);
            setRoles(userData.roles || ["general_user"]);
            setFullName(userData.full_name || null);
            setEmail(userData.email || null);
          } else {
            console.log("Auth state change - Backend fetch failed, using JWT");
            const decoded: any = jwtDecode(session.access_token);
            setRoles(decoded.app_metadata?.roles || ["general_user"]);
            setFullName(null);
            setEmail(decoded.email || null);
          }
        } catch (e) {
          console.error("Auth state change error:", e);
          const decoded: any = jwtDecode(session.access_token);
          setRoles(decoded.app_metadata?.roles || ["general_user"]);
          setFullName(null);
          setEmail(decoded.email || null);
        }
      } else {
        setRoles([]);
        setFullName(null);
        setEmail(null);
      }
    });

    return () => subscription.unsubscribe();
  }, [supabase.auth]);

  return { roles, fullName, email, loading, isAdmin: roles.includes("admin") };
}

export function RoleGuard({
  children,
  allowedRoles,
}: {
  children: React.ReactNode;
  allowedRoles: string[];
}) {
  const { roles, loading } = useRole();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading) {
      // Check if user has ANY of the allowed roles (OR logic)
      const hasAccess = roles.length > 0 && allowedRoles.some(r => roles.includes(r));
      if (!hasAccess) {
        // Redirect to dashboard if authorized but wrong role, or login if not auth
        if (roles.length > 0) {
          router.push("/dashboard");
        } else {
          router.push("/login");
        }
      }
    }
  }, [roles, loading, router, allowedRoles]);

  if (loading) return <div className="p-4">Checking permissions...</div>; // Or a spinner

  // Check if user has ANY of the allowed roles (OR logic)
  const hasAccess = roles.length > 0 && allowedRoles.some(r => roles.includes(r));
  if (!hasAccess) {
    return null; // Will redirect in useEffect
  }

  return <>{children}</>;
}
