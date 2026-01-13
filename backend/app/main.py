from fastapi import FastAPI
from app.routes.health import router as health_router
from app.routes.gmail_auth import router as gmail_auth_router
from app.routes import gmail_sync

app= FastAPI(title="Job Application Tracker")


app.include_router(gmail_auth_router)

app.include_router(gmail_sync.router)

app.include_router(health_router)

@app.get("/")
def root():
    return {"message":"Backend running successfully!"}