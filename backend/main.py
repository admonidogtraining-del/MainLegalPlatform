from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from database import engine, SessionLocal
import models
from routers import documents, scraper as scraper_router
from routers.scraper import run_full_scrape

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Legal Pulse API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(scraper_router.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# ── APScheduler: auto-scrape every 6 hours ──────────────────────────────────
def scheduled_scrape():
    db = SessionLocal()
    try:
        run_full_scrape(db)
    finally:
        db.close()


scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_scrape, "interval", hours=6, id="auto_scrape")
scheduler.start()
