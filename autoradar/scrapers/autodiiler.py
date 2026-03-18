import base64
import json
import logging
import re

from scrapers.base import BaseScraper, CarListing

logger = logging.getLogger(__name__)

# Autodiiler brand IDs (from garage.autodiiler.ee/api/v1/vehicles/misc/brands)
AUTODIILER_BRAND_IDS = {
    "bmw": 3, "audi": 2, "mercedes-benz": 18, "ford": 9, "opel": 21,
    "skoda": 29, "volvo": 33, "toyota": 32, "volkswagen": 34, "renault": 25,
    "peugeot": 22, "hyundai": 11, "kia": 13, "honda": 10, "mitsubishi": 19,
    "nissan": 20, "mazda": 17, "dacia": 55, "tesla": 61, "citroen": 5,
    "fiat": 8, "saab": 27, "seat": 28, "subaru": 30, "suzuki": 31,
    "jaguar": 12, "land rover": 50, "lexus": 16, "mini": 51, "porsche": 23,
}


class AutodiilerScraper(BaseScraper):
    """Scraper for autodiiler.ee.

    Verified from live site (2026-03):
    - Uses JSON API at garage.autodiiler.ee/api/v1/vehicles
    - Filters are base64-encoded JSON in the 'filters' query param
    - Results page: https://autodiiler.ee/en/vehicles?page=1&vt=1
    - Vehicle detail: https://autodiiler.ee/en/vehicles/{id}
    - API returns: id, name, price, registered_date, mileage, engine_power,
      transmission_type, drive_type, fuel_type, brand, brandModel, images, seo, location_name
    """

    PORTAL_NAME = "autodiiler"
    BASE_URL = "https://autodiiler.ee"
    API_URL = "https://garage.autodiiler.ee/api/v1/vehicles"

    def build_search_url(self, params: dict) -> str:
        """Build autodiiler.ee results page URL."""
        filters = {"page": "1", "vt": "1"}

        brand = params.get("brand", "").lower().strip()
        if brand:
            brand_id = AUTODIILER_BRAND_IDS.get(brand)
            if brand_id:
                filters["ba"] = str(brand_id)

        filters_b64 = base64.b64encode(json.dumps(filters).encode()).decode()
        return f"{self.API_URL}?locale=en&page=1&vt=1&filters={filters_b64}&s=default"

    async def scrape(self, params: dict) -> list[CarListing]:
        """Scrape autodiiler.ee via JSON API."""
        api_url = self.build_search_url(params)
        logger.info(f"[autodiiler] Scraping API: {api_url[:120]}...")

        page = await self._new_page()
        listings = []

        try:
            await self._random_delay(1.0, 3.0)
            response = await page.goto(api_url, wait_until="domcontentloaded", timeout=30000)

            if not response:
                logger.warning("[autodiiler] No response received")
                return listings

            status = response.status
            if status != 200:
                logger.warning(f"[autodiiler] Got status {status}")
                return listings

            text = await page.evaluate("() => document.body.innerText")
            data = json.loads(text)

            items = data.get("data", [])
            logger.info(f"[autodiiler] API returned {len(items)} items")

            year_min = params.get("year_min")
            year_max = params.get("year_max")
            price_min = params.get("price_min")
            price_max = params.get("price_max")
            mileage_max = params.get("mileage_max")
            exclude_keywords = [kw.strip().lower() for kw in params.get("exclude_keywords", "").split(",") if kw.strip()] if params.get("exclude_keywords") else []

            for item in items:
                try:
                    listing = self._parse_item(item)
                    if not listing:
                        continue
                    # Client-side filtering (API doesn't support these filters)
                    if year_min and listing.year and listing.year < year_min:
                        continue
                    if year_max and listing.year and listing.year > year_max:
                        continue
                    if price_min and listing.price and listing.price < price_min:
                        continue
                    if price_max and listing.price and listing.price > price_max:
                        continue
                    if mileage_max and listing.mileage and listing.mileage > mileage_max:
                        continue
                    if exclude_keywords and listing.title:
                        title_lower = listing.title.lower()
                        if any(kw in title_lower for kw in exclude_keywords):
                            continue
                    listings.append(listing)
                except Exception as e:
                    logger.debug(f"[autodiiler] Failed to parse item: {e}")

            logger.info(f"[autodiiler] Parsed {len(listings)} listings")

        except Exception as e:
            logger.error(f"[autodiiler] Scraping error: {e}")
        finally:
            await page.close()

        return listings

    def _parse_item(self, item: dict) -> CarListing | None:
        """Parse a single API result item into a CarListing."""
        item_id = item.get("id")
        if not item_id:
            return None

        external_id = str(item_id)
        name = item.get("name", "Unknown")
        price = item.get("price")
        mileage = item.get("mileage")

        # Year from registered_date (e.g. "2009-03-31T21:00:00.000000Z")
        year = None
        reg_date = item.get("registered_date", "")
        if reg_date:
            year_match = re.search(r"^(\d{4})", reg_date)
            if year_match:
                year = int(year_match.group(1))

        # Fuel type
        fuel_type = None
        fuel_data = item.get("fuel_type")
        if isinstance(fuel_data, dict):
            fuel_type = fuel_data.get("label")

        # Transmission
        transmission = None
        trans_data = item.get("transmission_type")
        if isinstance(trans_data, dict):
            transmission = trans_data.get("label")

        # Drive type
        drive_type = None
        drive_data = item.get("drive_type")
        if isinstance(drive_data, dict):
            drive_type = drive_data.get("label")

        # Body type
        body_type = None
        body_data = item.get("vehicleBodyType")
        if isinstance(body_data, dict):
            body_type = body_data.get("name")

        # Power
        power_kw = item.get("engine_power")

        # Location
        location = item.get("location_name")

        # Image
        image_url = None
        images = item.get("images", [])
        if images and isinstance(images, list):
            first_img = images[0]
            if isinstance(first_img, dict):
                image_url = first_img.get("thumbnail") or first_img.get("small")

        # SEO image fallback
        if not image_url:
            seo = item.get("seo")
            if isinstance(seo, dict):
                image_url = seo.get("image")

        # URL
        brand_data = item.get("brand", {})
        brand_slug = brand_data.get("slug", "") if isinstance(brand_data, dict) else ""
        url = f"{self.BASE_URL}/en/vehicles/{external_id}"

        return CarListing(
            portal="autodiiler",
            external_id=external_id,
            url=url,
            title=name,
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
