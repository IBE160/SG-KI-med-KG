from supabase import create_client, Client
from app.config import settings


def get_supabase_client() -> Client:
    """Get Supabase client instance with service role key for server-side operations."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables"
        )
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


supabase_client = get_supabase_client() if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY else None
