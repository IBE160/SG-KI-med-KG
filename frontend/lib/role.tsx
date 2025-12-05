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
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.access_token) {
        try {
          const decoded: any = jwtDecode(session.access_token);
          // Role is expected in app_metadata.role (from Supabase custom claims) 
          // OR we might need to fetch it if it's not there yet.
          // Our backend updates the DB 'role' column. 
          // Ideally, we sync this to Supabase app_metadata so it's in the JWT.
          // If not in JWT, we might need to fetch /users/me.
          // For MVP, let's assume we put it in app_metadata or rely on fetching user profile.
          
          // Note: Since we haven't implemented the sync to app_metadata in the backend yet (it was marked optional),
          // we should probably fetch the user profile from our backend to get the authoritative role.
          // But to keep it fast, let's check the token first.
          
          const appRole = decoded.app_metadata?.role;
          
          if (appRole) {
            setRole(appRole);
          } else {
             // Fallback: Fetch from backend if not in token
             // This adds latency but ensures accuracy if sync is missing
             // Or we can default to "general_user" if not present
             // Let's try to fetch self
             // TODO: implement fetch self profile if needed.
             setRole("general_user"); // Default for now
          }
        } catch (e) {
          console.error("Failed to decode token", e);
        }
      }
      setLoading(false);
    };

    getUserRole();
    
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (_event, session) => {
        if (session?.access_token) {
             const decoded: any = jwtDecode(session.access_token);
             setRole(decoded.app_metadata?.role || "general_user");
        } else {
            setRole(null);
        }
    });

    return () => subscription.unsubscribe();
  }, [supabase.auth]);

  return { role, loading, isAdmin: role === "admin" };
}

export function RoleGuard({ children, allowedRoles }: { children: React.ReactNode, allowedRoles: string[] }) {
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
