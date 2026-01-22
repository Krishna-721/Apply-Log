from fastapi import APIRouter
from app.gmail.service import get_gmail_service
from app.gmail.job_filter import classify_job_event, is_spam, is_allowed_sender
from app.gmail.body_parser import extract_email_body
from app.gmail.status_rank import should_update_status
from app.db import supabase
import time
import logging

from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError

router = APIRouter()

@router.post("/gmail/sync")
def gmail_sync(user_id: str):
    start_time = time.time()

    try:
        service = get_gmail_service(user_id)

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
        fetched_count = 0
        inserted_count = 0

        MAX_MESSAGES = 200

        while True:
            res = service.users().messages().list(
                userId="me",
                q=query,
                maxResults=50,
                pageToken=page_token
            ).execute()

            messages = res.get("messages", [])
            if not messages:
                break

            for msg in messages:
                if fetched_count >= MAX_MESSAGES:
                    break

                fetched_count += 1

                full = service.users().messages().get(
                    userId="me",
                    id=msg["id"],
                    format="full"
                ).execute()

                internal_date = int(full["internalDate"])
                newest_internal_date = max(newest_internal_date, internal_date)
                thread_id = full["threadId"]

                subject = ""
                sender = ""

                for h in full["payload"]["headers"]:
                    if h["name"] == "Subject":
                        subject = h["value"]
                    elif h["name"] == "From":
                        sender = h["value"]

                # Spam filter
                if is_spam(subject) and not is_allowed_sender(sender):
                    continue

                body = extract_email_body(full["payload"])
                status = classify_job_event(subject, body)
                if status is None:
                    continue

                # 2️⃣ Fetch application by thread
                existing_app = (
                    supabase.table("applications")
                    .select("id, current_status")
                    .eq("gmail_thread_id", thread_id)
                    .execute()
                    .data
                )

                if not existing_app:
                    # New application
                    app_res = supabase.table("applications").insert({
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

                    application_id = app_res.data[0]["id"]

                else:
                    application_id = existing_app[0]["id"]
                    current_status = existing_app[0]["current_status"]

                    if should_update_status(current_status, status):
                        supabase.table("applications").update({
                            "current_status": status,
                            "last_event_at": internal_date
                        }).eq("id", application_id).execute()

                # 🔁 EVENT-LEVEL DEDUP
                event_exists = (
                    supabase.table("application_events")
                    .select("id")
                    .eq("application_id", application_id)
                    .eq("gmail_message_id", msg["id"])
                    .execute()
                    .data
                )

                if not event_exists:
                    supabase.table("application_events").insert({
                        "application_id": application_id,
                        "gmail_message_id": msg["id"],
                        "gmail_thread_id": thread_id,
                        "event_type": status,
                        "subject": subject,
                        "sender": sender,
                        "occurred_at": internal_date,
                        "source": "gmail"
                    }).execute()


            page_token = res.get("nextPageToken")
            if not page_token or fetched_count >= MAX_MESSAGES:
                break

        # 4️⃣ Update cursor
        supabase.table("sync_state").upsert({
            "user_id": user_id,
            "last_internal_date": newest_internal_date
        }).execute()

        duration_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "status": "ok",
            "fetched": fetched_count,
            "processed": inserted_count,
            "new_events": newest_internal_date > last_internal_date,
            "duration_ms": duration_ms
        }

    except RefreshError:
        logging.warning(f"[GMAIL_SYNC] auth revoked for user={user_id}")
        return {
            "status": "auth_invalid",
            "processed": 0
        }

    except HttpError as e:
        logging.error(f"[GMAIL_SYNC] Gmail API error user={user_id}: {e}")
        return {
            "status": "gmail_error",
            "processed": 0
        }

    except Exception as e:
        logging.exception(f"[GMAIL_SYNC] Unexpected error user={user_id}")
        return {
            "status": "error",
            "error": str(e)
        }
