from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
import json
from supabase import supabase

from app.config import (
    GMAIL_CLIENT_ID,
    GMAIL_CLIENT_SECRET,
    GMAIL_REDIRECT_URI,
)

router = APIRouter()

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

CLIENT_CONFIG = {
    "web": {
        "client_id": GMAIL_CLIENT_ID,
        "client_secret": GMAIL_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [GMAIL_REDIRECT_URI],
    }
}


@router.get("/auth/gmail/login")
def gmail_login(user_id: str):
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=GMAIL_REDIRECT_URI,
    )

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=user_id,
    )

    return RedirectResponse(auth_url)


@router.get("/auth/gmail/callback")
def gmail_callback(request: Request):
    user_id=request.query_params.get("state")
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")
    
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=GMAIL_REDIRECT_URI,
    )

    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials

    # Store tokens per use in database
    supabase.table("gmail_tokens").upset({
        "user_id": user_id,
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": json.dumps(credentials.scopes),
    }).execute()

    return {
        "status": "gmail_connected",
        "user_id":user_id    
    }
