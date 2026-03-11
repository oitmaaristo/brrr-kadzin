import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import SessionLocal, create_tables
from backend.routers import filters, listings
from backend.scheduler import ScraperScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

scheduler = ScraperScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: start and stop scrapers."""
    # Startup
    create_tables()
    logger.info("Database tables created")

    await scheduler.start()
    scrape_task = asyncio.create_task(scheduler.run_loop())
    logger.info("Scraper scheduler started")

    yield

    # Shutdown
    await scheduler.stop()
    scrape_task.cancel()
    logger.info("Scraper scheduler stopped")


app = FastAPI(
    title="Autoradar",
    description="Kasutatud autode kuulutuste monitor Eesti portaalides",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(filters.router)
app.include_router(listings.router)


@app.get("/api/stats")
def get_stats():
    db = SessionLocal()
    try:
        from backend.database import Listing, SearchFilter

        total = db.query(Listing).count()
        notified = db.query(Listing).filter(Listing.notified_at.isnot(None)).count()
        active = db.query(SearchFilter).filter(SearchFilter.is_active.is_(True)).count()

        portal_counts = {}
        for portal in ["auto24", "autoportaal", "veego", "autodiiler"]:
            count = db.query(Listing).filter(Listing.portal == portal).count()
            if count > 0:
                portal_counts[portal] = count

        return {
            "total_listings": total,
            "total_notified": notified,
            "active_filters": active,
            "portal_counts": portal_counts,
            "last_scrape": scheduler.last_scrape,
        }
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"status": "ok", "last_scrape": scheduler.last_scrape}
