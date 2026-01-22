from fastapi import FastAPI
from app.routes.health import router as health_router
from app.routes.gmail_auth import router as gmail_auth_router
from app.routes import gmail_sync
# from app.routes.internal_sync import router as internal_sync_router
from app.routes.applications import router as application_router

app= FastAPI(title="Job Application Tracker")


app.include_router(gmail_auth_router)

app.include_router(gmail_sync.router)

# app.include_router(internal_sync_router)

app.include_router(application_router)

app.include_router(health_router)

@app.get("/")
def root():
    return {"message":"Backend running successfully!"}