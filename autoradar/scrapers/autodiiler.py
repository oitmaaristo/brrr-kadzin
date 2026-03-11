import logging
import re

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper, CarListing

logger = logging.getLogger(__name__)


class AutodiilerScraper(BaseScraper):
    """Scraper for autodiiler.ee.

    Operated by Webzero OU. URL structure needs verification on live site.
    Uses Playwright with broad CSS selectors and fallbacks.
    """

    PORTAL_NAME = "autodiiler"
    BASE_URL = "https://www.autodiiler.ee"

    def build_search_url(self, params: dict) -> str:
        """Build autodiiler.ee search URL."""
        query_parts = []

        brand = params.get("brand", "").lower()
        if brand:
            query_parts.append(f"make={brand}")

        model = params.get("model", "").lower()
        if model:
            query_parts.append(f"model={model}")

        if params.get("price_min"):
            query_parts.append(f"price_from={params['price_min']}")
        if params.get("price_max"):
            query_parts.append(f"price_to={params['price_max']}")
        if params.get("year_min"):
            query_parts.append(f"year_from={params['year_min']}")
        if params.get("year_max"):
            query_parts.append(f"year_to={params['year_max']}")

        url = f"{self.BASE_URL}/search"
        if query_parts:
            url += "?" + "&".join(query_parts)
        return url

    async def scrape(self, params: dict) -> list[CarListing]:
        """Scrape autodiiler.ee listings."""
        url = self.build_search_url(params)
        logger.info(f"[autodiiler] Scraping: {url}")

        page = await self._new_page()
        listings = []

        try:
            await self._random_delay(1.0, 3.0)
            response = await page.goto(url, wait_until="networkidle", timeout=30000)

            if not response:
                logger.warning("[autodiiler] No response received")
                return listings

            status = response.status
            if status == 403:
                logger.warning("[autodiiler] Got 403 - site may be blocking automated access")
                return listings
            if status != 200:
                logger.warning(f"[autodiiler] Got status {status}")
                return listings

            await self._random_delay(1.5, 3.0)

            html = await page.content()
            listings = self._parse_listings(html)

            if not listings:
                title = await page.title()
                logger.info(f"[autodiiler] Page title: {title}, HTML length: {len(html)}")

            logger.info(f"[autodiiler] Found {len(listings)} listings")

        except Exception as e:
            logger.error(f"[autodiiler] Scraping error: {e}")
        finally:
            await page.close()

        return listings

    def _parse_listings(self, html: str) -> list[CarListing]:
        """Parse listings from autodiiler.ee HTML."""
        soup = BeautifulSoup(html, "lxml")
        listings = []

        # Try multiple selector strategies
        rows = soup.select(".vehicle-item, .car-item, .listing-item, [class*='ad-card']")
        if not rows:
            rows = soup.select('[class*="vehicle"], [class*="listing"], [class*="car"]')
        if not rows:
            rows = soup.select("article, [class*='card'], [class*='item']")

        seen_ids = set()
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
                    url = f"{self.BASE_URL}{href}"
                else:
                    url = href

                external_id_match = re.search(r"/(\d+)", href)
                if not external_id_match:
                    external_id_match = re.search(r"[/-]([a-zA-Z0-9]{4,})$", href)
                if not external_id_match:
                    continue
                external_id = external_id_match.group(1)

                if external_id in seen_ids:
                    continue
                seen_ids.add(external_id)

                title_el = row.select_one("h2, h3, h4, .title, [class*='title'], [class*='name']")
                title = title_el.get_text(strip=True) if title_el else "Unknown"

                price = None
                price_el = row.select_one("[class*='price'], .price")
                if price_el:
                    digits = re.sub(r"[^\d]", "", price_el.get_text())
                    price = int(digits) if digits else None

                # Extract year and mileage from text
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
                        portal="autodiiler",
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
                logger.debug(f"[autodiiler] Failed to parse row: {e}")
                continue

        return listings
