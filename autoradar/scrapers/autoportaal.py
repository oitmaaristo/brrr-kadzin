import logging
import re

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper, CarListing

logger = logging.getLogger(__name__)


class AutoportaalScraper(BaseScraper):
    """Scraper for autoportaal.ee.

    URL patterns confirmed from search engine indexes:
    - Used cars listing: https://autoportaal.ee/en/used-cars
    - Brand filter: https://autoportaal.ee/en/{brand} (e.g., /en/bmw)
    - Brand+model: https://autoportaal.ee/en/{brand}-{model} (e.g., /en/bmw-x1)
    - Individual listing: /en/used-cars/{numeric_id}
    - Pagination: ?page=N (0-indexed)

    CSS selectors are best-guess and will be refined on first live run.
    """

    PORTAL_NAME = "autoportaal"
    BASE_URL = "https://autoportaal.ee/en/used-cars"

    def build_search_url(self, params: dict) -> str:
        """Build autoportaal.ee search URL."""
        brand = params.get("brand", "").lower().strip()
        model = params.get("model", "").lower().strip()

        # Brand+model uses path like /en/bmw-x1
        if brand and model:
            url = f"https://autoportaal.ee/en/{brand}-{model}"
        elif brand:
            url = f"https://autoportaal.ee/en/{brand}"
        else:
            url = self.BASE_URL

        # Query params (names are best-guess, to be refined on live site)
        query_parts = []
        if params.get("price_min"):
            query_parts.append(f"price_from={params['price_min']}")
        if params.get("price_max"):
            query_parts.append(f"price_to={params['price_max']}")
        if params.get("year_min"):
            query_parts.append(f"year_from={params['year_min']}")
        if params.get("year_max"):
            query_parts.append(f"year_to={params['year_max']}")

        if query_parts:
            url += "?" + "&".join(query_parts)

        return url

    async def scrape(self, params: dict) -> list[CarListing]:
        """Scrape autoportaal.ee listings."""
        url = self.build_search_url(params)
        logger.info(f"[autoportaal] Scraping: {url}")

        page = await self._new_page()
        listings = []

        try:
            await self._random_delay(1.0, 3.0)
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            if not response or response.status != 200:
                logger.warning(f"[autoportaal] Got status {response.status if response else 'None'}")
                return listings

            # Wait for content to load
            await self._random_delay(1.5, 3.0)

            html = await page.content()
            listings = self._parse_listings(html)
            logger.info(f"[autoportaal] Found {len(listings)} listings")

        except Exception as e:
            logger.error(f"[autoportaal] Scraping error: {e}")
        finally:
            await page.close()

        return listings

    def _parse_listings(self, html: str) -> list[CarListing]:
        """Parse listings from autoportaal.ee HTML.

        Uses broad selectors with fallbacks since exact CSS classes
        need to be verified against the live site.
        """
        soup = BeautifulSoup(html, "lxml")
        listings = []

        # Try multiple selector strategies
        rows = soup.select(".vehicle-item, .car-item, .listing-item, article.car")
        if not rows:
            rows = soup.select('[class*="vehicle"], [class*="listing"], [class*="car-card"]')
        if not rows:
            # Try finding any links to /en/used-cars/{id}
            rows = []
            for a_tag in soup.select('a[href*="/used-cars/"], a[href*="/kasutatud-autod/"]'):
                parent = a_tag.parent
                if parent and parent not in rows:
                    rows.append(parent)

        for row in rows:
            try:
                link_el = row.select_one("a[href]")
                if not link_el:
                    if row.name == "a":
                        link_el = row
                    else:
                        continue

                href = link_el.get("href", "")
                if not href:
                    continue

                if href.startswith("/"):
                    url = f"https://autoportaal.ee{href}"
                else:
                    url = href

                # Extract numeric ID from URL
                external_id_match = re.search(r"/(\d+)(?:\?|$|/)", href)
                if not external_id_match:
                    external_id_match = re.search(r"/(\d+)$", href)
                if not external_id_match:
                    continue
                external_id = external_id_match.group(1)

                title_el = row.select_one("h2, h3, h4, .title, [class*='title'], [class*='name']")
                title = title_el.get_text(strip=True) if title_el else "Unknown"

                price = None
                price_el = row.select_one("[class*='price'], .price")
                if price_el:
                    digits = re.sub(r"[^\d]", "", price_el.get_text())
                    price = int(digits) if digits else None

                # Try to extract year and mileage from text
                year = None
                mileage = None
                all_text = row.get_text(" ", strip=True)

                year_match = re.search(r"\b(19|20)\d{2}\b", all_text)
                if year_match:
                    year = int(year_match.group(0))

                km_match = re.search(r"([\d\s]+)\s*km", all_text)
                if km_match:
                    km_digits = re.sub(r"[^\d]", "", km_match.group(1))
                    if km_digits:
                        mileage = int(km_digits)

                img_el = row.select_one("img")
                image_url = img_el.get("src") or img_el.get("data-src") if img_el else None

                listings.append(
                    CarListing(
                        portal="autoportaal",
                        external_id=external_id,
                        url=url,
                        title=title,
                        price=price,
                        year=year,
                        mileage=mileage,
                        image_url=image_url,
                    )
                )
            except Exception as e:
                logger.debug(f"[autoportaal] Failed to parse row: {e}")
                continue

        return listings
