from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app.db import supabase
import json

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service(user_id: str):
    res = (
        supabase.table("gmail_tokens")
        .select("*")
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    token_data = res.data
    if not token_data:
        raise RuntimeError("No Gmail token found for user")

    creds = Credentials(
        token=token_data["token"],
        refresh_token=token_data["refresh_token"],
        token_uri=token_data["token_uri"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        scopes=json.loads(token_data["scopes"]),
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

        # 🔥 Persist refreshed token
        supabase.table("gmail_tokens").update({
            "token": creds.token,
            "updated_at": "now()"
        }).eq("user_id", user_id).execute()

    return build("gmail", "v1", credentials=creds)
