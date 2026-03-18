import asyncio
import logging
import random
import traceback
from datetime import datetime

from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import Listing, PriceHistory, SearchFilter, SessionLocal
from bot.notifications import send_listing_notification, send_price_change_notification, send_status_message
from scrapers.auto24 import Auto24Scraper
from scrapers.autoportaal import AutoportaalScraper
from scrapers.autodiiler import AutodiilerScraper
from scrapers.base import BaseScraper, CarListing
from scrapers.veego import VeegoScraper

logger = logging.getLogger(__name__)

# Map portal names to scraper classes
SCRAPER_CLASSES: dict[str, type[BaseScraper]] = {
    "auto24": Auto24Scraper,
    "autoportaal": AutoportaalScraper,
    "veego": VeegoScraper,
    "autodiiler": AutodiilerScraper,
}

# Max consecutive errors before backing off a portal
MAX_CONSECUTIVE_ERRORS = 5


class ScraperScheduler:
    """Manages scraping cycles across all portals."""

    def __init__(self):
        self._scrapers: dict[str, BaseScraper] = {}
        self._running = False
        self._last_scrape: datetime | None = None
        self._consecutive_errors: dict[str, int] = {}

    async def start(self):
        """Initialize all scrapers. Skip portals that fail to start."""
        for name, cls in SCRAPER_CLASSES.items():
            try:
                scraper = cls()
                await scraper.start()
                self._scrapers[name] = scraper
                self._consecutive_errors[name] = 0
                logger.info(f"[{name}] Scraper initialized")
            except Exception as e:
                logger.error(f"[{name}] Failed to start scraper: {e}")
        logger.info(f"Scrapers initialized: {list(self._scrapers.keys())}")

    async def stop(self):
        """Stop all scrapers."""
        self._running = False
        for name, scraper in self._scrapers.items():
            try:
                await scraper.stop()
            except Exception as e:
                logger.error(f"[{name}] Error stopping scraper: {e}")
        logger.info("All scrapers stopped")

    async def run_loop(self):
        """Main scraping loop - runs until stopped."""
        self._running = True
        await send_status_message("Autoradar kaivitatud! Jalgin kuulutusi...")

        while self._running:
            try:
                await self._scrape_cycle()
            except Exception as e:
                logger.error(f"Scrape cycle error: {e}\n{traceback.format_exc()}")

            # Random delay between cycles
            delay = random.randint(settings.poll_interval_min, settings.poll_interval_max)
            logger.info(f"Next scrape in {delay} seconds")
            await asyncio.sleep(delay)

    async def _scrape_cycle(self):
        """Run one scraping cycle across all active filters."""
        db = SessionLocal()
        try:
            filters = (
                db.query(SearchFilter)
                .filter(SearchFilter.is_active.is_(True))
                .all()
            )

            if not filters:
                logger.debug("No active filters, skipping cycle")
                return

            for search_filter in filters:
                portals = search_filter.portals or ["auto24"]
                params = search_filter.params or {}

                for portal in portals:
                    scraper = self._scrapers.get(portal)
                    if not scraper:
                        continue

                    # Skip portal if too many consecutive errors (back off)
                    errors = self._consecutive_errors.get(portal, 0)
                    if errors >= MAX_CONSECUTIVE_ERRORS:
                        # Exponential backoff: skip this portal for a while
                        # After 5 errors, restart the scraper browser
                        logger.warning(
                            f"[{portal}] {errors} consecutive errors, restarting browser..."
                        )
                        try:
                            await scraper.stop()
                            await scraper.start()
                            self._consecutive_errors[portal] = 0
                        except Exception as e:
                            logger.error(f"[{portal}] Failed to restart: {e}")
                            continue

                    try:
                        listings = await scraper.scrape(params)
                        new_count = await self._process_listings(db, listings)
                        self._consecutive_errors[portal] = 0

                        if new_count > 0:
                            logger.info(
                                f"[{portal}] {new_count} new listings for filter '{search_filter.name}'"
                            )
                    except Exception as e:
                        self._consecutive_errors[portal] = errors + 1
                        logger.error(
                            f"[{portal}] Scrape error for filter '{search_filter.name}' "
                            f"(errors: {errors + 1}): {e}"
                        )

                    # Small delay between portals
                    await asyncio.sleep(random.uniform(2, 5))

            self._last_scrape = datetime.utcnow()

        finally:
            db.close()

    async def _process_listings(self, db: Session, listings: list[CarListing]) -> int:
        """Process scraped listings: save new ones, update existing, send notifications.

        Returns:
            Number of new listings found.
        """
        new_count = 0

        for car in listings:
            try:
                # Check if we already have this listing
                existing = (
                    db.query(Listing)
                    .filter(
                        Listing.portal == car.portal,
                        Listing.external_id == car.external_id,
                    )
                    .first()
                )

                if existing:
                    # Update price if changed (price tracking)
                    if car.price and existing.price and car.price != existing.price:
                        old_price = existing.price
                        logger.info(
                            f"[{car.portal}] Price changed for {car.title}: "
                            f"{old_price} -> {car.price}"
                        )

                        # Record price history
                        price_record = PriceHistory(
                            listing_id=existing.id,
                            old_price=old_price,
                            new_price=car.price,
                        )
                        db.add(price_record)
                        existing.price = car.price
                        db.commit()

                        # Send price change notification
                        try:
                            listing_dict = {
                                "portal": existing.portal,
                                "title": existing.title,
                                "price": car.price,
                                "old_price": old_price,
                                "year": existing.year,
                                "mileage": existing.mileage,
                                "url": existing.url,
                            }
                            await send_price_change_notification(listing_dict)
                        except Exception as e:
                            logger.error(f"Failed to notify price change for listing {existing.id}: {e}")

                    continue

                # New listing - save to DB
                listing = Listing(
                    portal=car.portal,
                    external_id=car.external_id,
                    url=car.url,
                    title=car.title,
                    price=car.price,
                    year=car.year,
                    mileage=car.mileage,
                    fuel_type=car.fuel_type,
                    transmission=car.transmission,
                    body_type=car.body_type,
                    engine_volume=car.engine_volume,
                    power_kw=car.power_kw,
                    drive_type=car.drive_type,
                    color=car.color,
                    location=car.location,
                    seller_type=car.seller_type,
                    image_url=car.image_url,
                    reg_number=car.reg_number,
                    raw_data=car.raw_data,
                )
                db.add(listing)
                db.commit()
                db.refresh(listing)

                # Send Telegram notification
                try:
                    listing_dict = {
                        "portal": listing.portal,
                        "title": listing.title,
                        "price": listing.price,
                        "year": listing.year,
                        "mileage": listing.mileage,
                        "fuel_type": listing.fuel_type,
                        "transmission": listing.transmission,
                        "location": listing.location,
                        "url": listing.url,
                        "image_url": listing.image_url,
                    }
                    await send_listing_notification(listing_dict)
                    listing.notified_at = datetime.utcnow()
                    db.commit()
                except Exception as e:
                    logger.error(f"Failed to notify for listing {listing.id}: {e}")

                new_count += 1

            except Exception as e:
                logger.error(f"Error processing listing {car.external_id}: {e}")
                db.rollback()
                continue

        return new_count

    @property
    def last_scrape(self) -> datetime | None:
        return self._last_scrape
