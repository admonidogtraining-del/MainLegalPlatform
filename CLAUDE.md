# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Legal Pulse** - A full-stack platform for tracking and analyzing Israeli legal documents (legislation, court rulings, and bills). Content is in Hebrew with RTL layout.

## Commands

### Frontend (in `frontend/`)
```bash
npm run dev      # Dev server at http://localhost:5173
npm run build    # Production build
npm run preview  # Preview production build
```

### Backend (in `backend/`)
```bash
uvicorn main:app --reload   # Dev server at http://localhost:8000
python seed.py              # Seed sample data (run from root)
```

Both servers must run simultaneously. Vite proxies `/api` requests to `localhost:8000`.

## Architecture

**Frontend**: React 18 + Vite + Tailwind CSS. All state lives in `App.jsx` using hooks. `src/services/api.js` is the single Axios client. Court filtering is done client-side after API fetch (backend doesn't support it as a query param).

**Backend**: FastAPI with SQLAlchemy (SQLite). Two routers: `routers/documents.py` (CRUD) and `routers/scraper.py` (scraping orchestration). Scrapers in `scrapers/` fetch from Knesset and court websites.

**Auto-scraping**: APScheduler in `main.py` runs all scrapers every 6 hours. Manual trigger via `POST /api/scrape`. Deduplication uses `source_url` or `title+pub_date` composite.

## Data Model

Single `Document` model (`backend/models.py`) covers all content types:
- `type`: `legislation` | `ruling` | `bill`
- `urgency`: `high` | `medium` | `low`
- `scraped_from`: `knesset` | `elyon1` | `supreme` | `manual`
- `law_area`: comma-separated Hebrew categories
- `pub_date`: DD/MM/YYYY string format

## API Endpoints

```
GET    /api/documents              # List (query: type, urgency, bookmarked, search)
GET    /api/documents/stats        # Dashboard stats
GET    /api/documents/{id}
POST   /api/documents
PATCH  /api/documents/{id}/bookmark
PATCH  /api/documents/{id}/urgency
DELETE /api/documents/{id}
POST   /api/scrape                 # Manual scrape trigger (background task)
GET    /api/scrape/status          # Last run time, count, running status (resets on restart)
GET    /api/health
```

## Key Conventions

- Hebrew UI with RTL layout (`dir="rtl"` in `index.html`, global CSS in `frontend/src/index.css`)
- Font: Heebo (Google Fonts)
- CORS is configured for `localhost:5173` only
- Scrape status (last_run, count, is_running) is in-memory — resets on server restart
