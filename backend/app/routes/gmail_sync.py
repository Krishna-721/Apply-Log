from fastapi import APIRouter
from app.gmail.service import get_gmail_service,should_update_status
from app.gmail.job_filter import classify_job_event, is_spam, is_allowed_sender
from app.gmail.body_parser import extract_email_body
from app.db import supabase
import time

router = APIRouter()

@router.post("/gmail/sync")
def gmail_sync(user_id: str):
    service = get_gmail_service()
    start_time = time.time()

    # 1️⃣ Get last sync cursor
    cursor_res = (
        supabase.table("sync_state")
        .select("last_internal_date")
        .eq("user_id", user_id)
        .execute()
    )

    last_internal_date = cursor_res.data[0]["last_internal_date"] if cursor_res.data else 0
    query = "" if last_internal_date == 0 else f"after:{last_internal_date // 1000}"

    page_token = None
    newest_internal_date = last_internal_date
    inserted_count = 0
    fetched_count = 0

    while True:
        res = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=50,
            pageToken=page_token
        ).execute()

        messages = res.get("messages", [])
        fetched_count += len(messages)

        for msg in messages:
            full = service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="full"
            ).execute()

            internal_date = int(full["internalDate"])
            newest_internal_date = max(newest_internal_date, internal_date)

            thread_id = full["threadId"]

            # 2️⃣ Extract headers
            subject = ""
            sender = ""

            for h in full["payload"]["headers"]:
                if h["name"] == "Subject":
                    subject = h["value"]
                elif h["name"] == "From":
                    sender = h["value"]

            # 3️⃣ Hard spam filter
            if is_spam(subject) and not is_allowed_sender(sender):
                continue

            body = extract_email_body(full["payload"])
            status = classify_job_event(subject, body)

            if status is None:
                continue

            # 4️⃣ Thread-based dedup
            existing_app = (
                supabase.table("applications")
                .select("id, current_status")
                .eq("gmail_thread_id", thread_id)
                .execute()
                .data
            )

            if not existing_app:
                # 5️⃣ Insert new application
                supabase.table("applications").insert({
                    "user_id": user_id,
                    "gmail_thread_id": thread_id,
                    "gmail_message_id": msg["id"],
                    "gmail_internal_date": internal_date,
                    "company": sender,
                    "role": subject,
                    "status": status,
                    "current_status": status,
                    "last_event_at": internal_date,
                    "source": "gmail"
                }).execute()

                inserted_count += 1

            else:
                # 6️⃣ Update existing application
                current_status = existing_app[0]["current_status"]

                if should_update_status(current_status, status):
                    supabase.table("applications").update({
                        "current_status": status,
                        "last_event_at": internal_date
                    }).eq("gmail_thread_id", thread_id).execute()


        page_token = res.get("nextPageToken")
        if not page_token:
            break

    # 7️⃣ Update sync cursor
    supabase.table("sync_state").upsert({
        "user_id": user_id,
        "last_internal_date": newest_internal_date
    }).execute()

    duration_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "fetched": fetched_count,
        "processed": inserted_count,
        "new_events": newest_internal_date > last_internal_date,
        "duration_ms": duration_ms
    }
