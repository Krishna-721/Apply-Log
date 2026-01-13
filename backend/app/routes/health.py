from fastapi import APIRouter
from app.gmail.service import get_gmail_service
from app.gmail.job_filter import classify_job_event
from app.gmail.body_parser import extract_email_body

router = APIRouter()

@router.get("/gmail/test")
def gmail_test():
    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        q="",
        includeSpamTrash=True,
        maxResults=200
    ).execute()

    messages = results.get("messages", [])
    output = []

    for msg in messages:
        full = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        # --- Extract headers ---
        subject = ""
        sender = ""

        for h in full["payload"]["headers"]:
            if h["name"] == "Subject":
                subject = h["value"]
            elif h["name"] == "From":
                sender = h["value"]

        # --- Extract decoded body ---
        body = extract_email_body(full["payload"])

        # --- Classify lifecycle event ---
        status = classify_job_event(subject, body)

        if status is None:
            continue

        output.append({
            "id": msg["id"],
            "subject": subject,
            "from": sender,
            "status": status
        })

    return output
