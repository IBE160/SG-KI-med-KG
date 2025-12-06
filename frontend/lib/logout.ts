import { createClient } from "@/lib/supabase";

export async function logout() {
  const supabase = createClient();

  // Sign out from Supabase (clears session and local storage)
  const { error } = await supabase.auth.signOut();

  if (error) {
    console.error("Logout error:", error);
    throw error;
  }

  return { success: true };
}
