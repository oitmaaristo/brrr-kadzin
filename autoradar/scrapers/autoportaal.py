import logging
import re

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper, CarListing

logger = logging.getLogger(__name__)


class AutoportaalScraper(BaseScraper):
    """Scraper for autoportaal.ee.

    Verified URL and selectors from live site (2026-03):
    - Search: https://autoportaal.ee/en/used-cars (no working query param filtering)
    - Brand filter via path: https://autoportaal.ee/en/{brand}
    - Individual listing: /en/used-cars/{numeric_id}
    - Listing container: div.advertisement
    - Title: h2 inside .dataBlock
    - Price: div.finalPrice span
    - Year: li.year, Mileage: li.mileage, Fuel: li.fuel, Gearbox: li.gearbox
    - Drive: li.drive, Body: li.body_type
    - Location: div.location
    - Link: a.dataArea[href]
    - ID: from span[id^="f"] (favorites) or URL /used-cars/{id}
    - Image: img inside .photoAreaContainer
    """

    PORTAL_NAME = "autoportaal"
    BASE_URL = "https://autoportaal.ee"

    def build_search_url(self, params: dict) -> str:
        """Build autoportaal.ee search URL using path-based brand filter.

        Includes type[]=1 (cars+SUVs) and type[]=2 (vans) to exclude
        motorcycles, boats, trailers, etc.
        """
        brand = params.get("brand", "").lower().strip()
        model = params.get("model", "").lower().strip()

        if brand and model:
            url = f"{self.BASE_URL}/en/{brand}-{model}"
        elif brand:
            url = f"{self.BASE_URL}/en/{brand}"
        else:
            url = f"{self.BASE_URL}/en/used-cars"

        # Filter to cars+SUVs and vans only
        url += "?type[]=1&type[]=2"

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

            await self._random_delay(1.5, 3.0)

            html = await page.content()
            listings = self._parse_listings(html, params)
            logger.info(f"[autoportaal] Found {len(listings)} listings")

        except Exception as e:
            logger.error(f"[autoportaal] Scraping error: {e}")
        finally:
            await page.close()

        return listings

    def _parse_listings(self, html: str, params: dict) -> list[CarListing]:
        """Parse listings from autoportaal.ee HTML."""
        soup = BeautifulSoup(html, "lxml")
        listings = []

        rows = soup.select("div.advertisement")
        if not rows:
            logger.info("[autoportaal] No .advertisement elements found")
            return listings

        year_min = params.get("year_min")
        year_max = params.get("year_max")
        price_max = params.get("price_max")
        price_min = params.get("price_min")
        mileage_max = params.get("mileage_max")
        exclude_keywords = [kw.strip().lower() for kw in params.get("exclude_keywords", "").split(",") if kw.strip()] if params.get("exclude_keywords") else []

        seen_ids = set()
        for row in rows:
            try:
                # Link and URL
                link_el = row.select_one("a.dataArea")
                if not link_el:
                    link_el = row.select_one("a[href*='/used-cars/']")
                if not link_el:
                    continue

                href = link_el.get("href", "")
                if not href:
                    continue

                url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

                # Extract ID from URL or favorites span
                external_id = None
                fav_el = row.select_one("span[id^='f']")
                if fav_el:
                    external_id = fav_el.get("id", "")[1:]
                if not external_id:
                    id_match = re.search(r"/used-cars/(\d+)", href)
                    if id_match:
                        external_id = id_match.group(1)
                if not external_id:
                    continue

                if external_id in seen_ids:
                    continue
                seen_ids.add(external_id)

                # Title from h2 inside dataBlock
                title = "Unknown"
                data_block = row.select_one(".dataBlock")
                if data_block:
                    h2 = data_block.select_one("h2")
                    if h2:
                        title = h2.get_text(strip=True)

                # Price
                price = None
                price_el = row.select_one(".finalPrice")
                if price_el:
                    digits = re.sub(r"[^\d]", "", price_el.get_text())
                    price = int(digits) if digits else None

                # Year
                year = None
                year_el = row.select_one("li.year")
                if year_el:
                    year_text = year_el.get_text(strip=True)
                    year_match = re.search(r"\d{4}", year_text)
                    if year_match:
                        year = int(year_match.group(0))

                # Client-side filtering (autoportaal URL params don't filter)
                if year_min and year and year < year_min:
                    continue
                if year_max and year and year > year_max:
                    continue
                if price_max and price and price > price_max:
                    continue
                if price_min and price and price < price_min:
                    continue

                # Mileage (parse early for filtering)
                mileage = None
                mileage_el = row.select_one("li.mileage")
                if mileage_el:
                    km_digits = re.sub(r"[^\d]", "", mileage_el.get_text())
                    mileage = int(km_digits) if km_digits else None

                if mileage_max and mileage and mileage > mileage_max:
                    continue

                # Exclude keywords filter
                if exclude_keywords and title:
                    title_lower = title.lower()
                    if any(kw in title_lower for kw in exclude_keywords):
                        continue

                # Fuel type
                fuel_type = None
                fuel_el = row.select_one("li.fuel")
                if fuel_el:
                    fuel_text = fuel_el.get_text(strip=True)
                    if fuel_text and fuel_text not in ("-",):
                        fuel_type = fuel_text

                # Transmission
                transmission = None
                gearbox_el = row.select_one("li.gearbox")
                if gearbox_el:
                    transmission = gearbox_el.get_text(strip=True) or None

                # Drive type
                drive_type = None
                drive_el = row.select_one("li.drive")
                if drive_el:
                    drive_text = drive_el.get_text(strip=True)
                    if drive_text and drive_text not in ("-",):
                        drive_type = drive_text

                # Body type
                body_type = None
                body_el = row.select_one("li.body_type")
                if body_el:
                    body_type = body_el.get_text(strip=True) or None

                # Power
                power_kw = None
                power_el = row.select_one("li.power_kw")
                if power_el:
                    kw_match = re.search(r"(\d+)\s*kW", power_el.get_text())
                    if kw_match:
                        power_kw = int(kw_match.group(1))

                # Location
                location = None
                loc_el = row.select_one(".location")
                if loc_el:
                    location = loc_el.get_text(strip=True) or None

                # Image
                image_url = None
                img_el = row.select_one("img")
                if img_el:
                    image_url = img_el.get("src") or img_el.get("data-src")

                listings.append(
                    CarListing(
                        portal="autoportaal",
                        external_id=external_id,
                        url=url,
                        title=title,
                        price=price,
                        year=year,
                        mileage=mileage,
                        fuel_type=fuel_type,
                        transmission=transmission,
                        body_type=body_type,
                        power_kw=power_kw,
                        drive_type=drive_type,
                        location=location,
                        image_url=image_url,
                    )
                )
            except Exception as e:
                logger.debug(f"[autoportaal] Failed to parse row: {e}")
                continue

        return listings
