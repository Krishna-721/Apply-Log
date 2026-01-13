from fastapi import APIRouter
from app.db import supabase

router = APIRouter(prefix="/applications", tags=["applications"])

@router.get("/")
def list_applications(
    user_id: str,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0
):
    query = (
        supabase.table("applications")
        .select(
            "id,company,role,current_status,last_event_at,source"
        )
        .eq("user_id", user_id)
        .order("last_event_at", desc=True)
        .range(offset, offset + limit - 1)
    )

    if status:
        query = query.eq("current_status", status)

    res = query.execute()
    return res.data

@router.get("/{application_id}")
def get_application(application_id: str, user_id: str):
    res = (
        supabase.table("applications")
        .select("*")
        .eq("id", application_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    return res.data


@router.get("/{application_id}/timeline")
def application_timeline(application_id: str, user_id: str):
    res = (
        supabase.table("application_events")
        .select(
            "event_type, subject, sender, occurred_at, source"
        )
        .eq("application_id", application_id)
        .order("occurred_at", desc=False)
        .execute()
    )
    return res.data
