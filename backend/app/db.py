import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_ROLE_KEY = os.getenv("SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SERVICE_ROLE_KEY:
    raise RuntimeError("Supabase environment variables not set")

supabase: Client = create_client(
    SUPABASE_URL,
    SERVICE_ROLE_KEY)
