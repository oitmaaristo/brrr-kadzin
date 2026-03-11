import logging
import re

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper, CarListing

logger = logging.getLogger(__name__)


class AutoportaalScraper(BaseScraper):
    """Scraper for autoportaal.ee."""

    PORTAL_NAME = "autoportaal"
    BASE_URL = "https://www.autoportaal.ee/kasutatud-autod"

    def build_search_url(self, params: dict) -> str:
        """Build autoportaal.ee search URL.

        Note: autoportaal.ee URL structure needs to be mapped
        by inspecting the site's search form. This is a placeholder
        that will be refined once we can access the site.
        """
        # autoportaal uses path-based filtering
        parts = [self.BASE_URL]

        brand = params.get("brand", "").lower()
        if brand:
            parts.append(brand)

        model = params.get("model", "").lower()
        if model:
            parts.append(model)

        url = "/".join(parts)

        # Query params for additional filters
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

            await self._random_delay(1.0, 2.0)
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

        Note: Selectors need to be verified against the actual site.
        """
        soup = BeautifulSoup(html, "lxml")
        listings = []

        # Common patterns for car listing sites
        rows = soup.select(".vehicle-item, .car-item, .listing-item, article.car")
        if not rows:
            rows = soup.select('[class*="vehicle"], [class*="listing"], [class*="car-card"]')

        for row in rows:
            try:
                link_el = row.select_one("a[href]")
                if not link_el:
                    continue

                href = link_el.get("href", "")
                if not href:
                    continue

                if href.startswith("/"):
                    url = f"https://www.autoportaal.ee{href}"
                else:
                    url = href

                external_id = re.search(r"/(\d+)", href)
                if not external_id:
                    continue
                external_id = external_id.group(1)

                title_el = row.select_one("h2, h3, .title, .vehicle-title")
                title = title_el.get_text(strip=True) if title_el else "Unknown"

                price = None
                price_el = row.select_one(".price, [class*='price']")
                if price_el:
                    digits = re.sub(r"[^\d]", "", price_el.get_text())
                    price = int(digits) if digits else None

                img_el = row.select_one("img")
                image_url = img_el.get("src") or img_el.get("data-src") if img_el else None

                listings.append(
                    CarListing(
                        portal="autoportaal",
                        external_id=external_id,
                        url=url,
                        title=title,
                        price=price,
                        image_url=image_url,
                    )
                )
            except Exception as e:
                logger.debug(f"[autoportaal] Failed to parse row: {e}")
                continue

        return listings
