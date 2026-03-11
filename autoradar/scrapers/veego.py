import logging
import re

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper, CarListing

logger = logging.getLogger(__name__)


class VeegoScraper(BaseScraper):
    """Scraper for veego.ee."""

    PORTAL_NAME = "veego"
    BASE_URL = "https://www.veego.ee/search"

    def build_search_url(self, params: dict) -> str:
        """Build veego.ee search URL.

        Note: URL structure needs to be verified against the actual site.
        """
        query_parts = []

        brand = params.get("brand", "").lower()
        if brand:
            query_parts.append(f"make={brand}")

        model = params.get("model", "").lower()
        if model:
            query_parts.append(f"model={model}")

        if params.get("price_min"):
            query_parts.append(f"price_min={params['price_min']}")
        if params.get("price_max"):
            query_parts.append(f"price_max={params['price_max']}")
        if params.get("year_min"):
            query_parts.append(f"year_min={params['year_min']}")
        if params.get("year_max"):
            query_parts.append(f"year_max={params['year_max']}")

        url = self.BASE_URL
        if query_parts:
            url += "?" + "&".join(query_parts)
        return url

    async def scrape(self, params: dict) -> list[CarListing]:
        """Scrape veego.ee listings."""
        url = self.build_search_url(params)
        logger.info(f"[veego] Scraping: {url}")

        page = await self._new_page()
        listings = []

        try:
            await self._random_delay(1.0, 3.0)
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            if not response or response.status != 200:
                logger.warning(f"[veego] Got status {response.status if response else 'None'}")
                return listings

            await self._random_delay(1.0, 2.0)
            html = await page.content()
            listings = self._parse_listings(html)
            logger.info(f"[veego] Found {len(listings)} listings")

        except Exception as e:
            logger.error(f"[veego] Scraping error: {e}")
        finally:
            await page.close()

        return listings

    def _parse_listings(self, html: str) -> list[CarListing]:
        """Parse listings from veego.ee HTML."""
        soup = BeautifulSoup(html, "lxml")
        listings = []

        rows = soup.select(".vehicle-card, .car-card, .listing-card, [class*='vehicle-item']")
        if not rows:
            rows = soup.select('[class*="car"], [class*="listing"], [class*="vehicle"]')

        for row in rows:
            try:
                link_el = row.select_one("a[href]")
                if not link_el:
                    continue

                href = link_el.get("href", "")
                if not href:
                    continue

                if href.startswith("/"):
                    url = f"https://www.veego.ee{href}"
                else:
                    url = href

                external_id = re.search(r"/(\d+)", href)
                if not external_id:
                    external_id = re.search(r"[/-]([a-zA-Z0-9]+)$", href)
                if not external_id:
                    continue
                external_id = external_id.group(1)

                title_el = row.select_one("h2, h3, .title, [class*='title']")
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
                        portal="veego",
                        external_id=external_id,
                        url=url,
                        title=title,
                        price=price,
                        image_url=image_url,
                    )
                )
            except Exception as e:
                logger.debug(f"[veego] Failed to parse row: {e}")
                continue

        return listings
