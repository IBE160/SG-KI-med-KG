import { client } from "@/app/openapi-client/sdk.gen";
import { createClient as createSupabaseClient } from "@/lib/supabase";

let interceptorAdded = false;

const configureClient = () => {
  const baseURL =
    process.env.NEXT_PUBLIC_API_URL ||
    process.env.API_BASE_URL ||
    "http://localhost:8000";

  client.setConfig({
    baseURL: baseURL,
  });
};

// Setup auth interceptor - call this from client-side code
export const setupAuthInterceptor = () => {
  if (interceptorAdded || typeof window === "undefined" || !client.instance) {
    return;
  }

  client.instance.interceptors.request.use(async (config) => {
    try {
      const supabase = createSupabaseClient();
      const { data: { session } } = await supabase.auth.getSession();

      if (session?.access_token) {
        config.headers = config.headers || {};
        config.headers.Authorization = `Bearer ${session.access_token}`;
      }
    } catch (e) {
      // Ignore auth errors when not logged in
    }

    return config;
  });

  interceptorAdded = true;
};

configureClient();

// Auto-setup on client side
if (typeof window !== "undefined") {
  setupAuthInterceptor();
}
