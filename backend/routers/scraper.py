from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from scrapers.knesset_bills import scrape_bills
from scrapers.knesset_laws import scrape_laws
from scrapers.court_decisions import scrape_court_decisions
from scrapers.psakdin import scrape_psakdin
from scrapers.nevo import scrape_nevo
from datetime import datetime

router = APIRouter(prefix="/api/scrape", tags=["scraper"])

# Simple in-memory state (resets on server restart)
_scrape_state = {
    "last_run": None,
    "last_count": 0,
    "is_running": False,
}


def _upsert_documents(records: list, db: Session) -> int:
    """Insert records that don't already exist (dedup by source_url or title+pub_date)."""
    added = 0
    for rec in records:
        # Dedup: skip if same source_url already exists
        if rec.get("source_url"):
            exists = (
                db.query(models.Document)
                .filter(models.Document.source_url == rec["source_url"])
                .first()
            )
            if exists:
                continue
        else:
            # fallback dedup: same title + pub_date
            exists = (
                db.query(models.Document)
                .filter(
                    models.Document.title == rec.get("title"),
                    models.Document.pub_date == rec.get("pub_date"),
                )
                .first()
            )
            if exists:
                continue

        doc = models.Document(**{k: v for k, v in rec.items() if hasattr(models.Document, k)})
        db.add(doc)
        added += 1

    db.commit()
    return added


def run_full_scrape(db: Session):
    """Run all scrapers and save results. Called by scheduler and manual trigger."""
    _scrape_state["is_running"] = True
    total = 0
    try:
        for scraper_fn in [scrape_bills, scrape_laws, scrape_court_decisions, scrape_psakdin, scrape_nevo]:
            try:
                records = scraper_fn()
                added = _upsert_documents(records, db)
                total += added
                print(f"[scraper] {scraper_fn.__name__}: fetched {len(records)}, added {added}")
            except Exception as e:
                print(f"[scraper] {scraper_fn.__name__} error: {e}")
    finally:
        _scrape_state["is_running"] = False
        _scrape_state["last_run"] = datetime.utcnow().isoformat()
        _scrape_state["last_count"] = total
    return total


@router.post("", response_model=schemas.ScrapeStatus)
def trigger_scrape(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger a full scrape run in the background."""
    if _scrape_state["is_running"]:
        return schemas.ScrapeStatus(**_scrape_state)
    background_tasks.add_task(run_full_scrape, db)
    _scrape_state["is_running"] = True
    return schemas.ScrapeStatus(**_scrape_state)


@router.get("/status", response_model=schemas.ScrapeStatus)
def scrape_status():
    return schemas.ScrapeStatus(**_scrape_state)
