import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service():
    with open("gmail_token.json","r") as f:
        token_data=json.load(f)

    creds = Credentials(
        token=token_data['token'],
        refresh_token=token_data["refresh_token"],
        token_uri=token_data["token_uri"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        scopes=SCOPES,
    )

    service=build("gmail","v1",credentials=creds)
    return service