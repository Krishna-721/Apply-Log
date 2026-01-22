from fastapi import APIRouter, Header, HTTPException
from app.routes.gmail_sync import gmail_sync
from app.config import CRON_SECRET
from app.db import supabase
#import os

router = APIRouter()

#CRON_SECRET=os.getenv("CRON_SECRET")

@router.post("/internal/gmail/sync-all")
def sync_all_gmail(x_cron_secret: str = Header(None, alias="x-cron-secret")):
    
    print("Received: ",x_cron_secret)
    print("Expected: ",CRON_SECRET)
    
    if x_cron_secret!=CRON_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    users = (
    supabase.table("sync_state")
    .select("user_id")
    .execute()
    .data
)

    results=[]

    for row in users:
        res = gmail_sync(row["user_id"])
        results.append({
            "user_id": row["user_id"],
            "status": res.get("status","ok"),
            "processed": res.get("processed",0)
        })

    return{
        "synced_users":len(results),
        "results":results
    }