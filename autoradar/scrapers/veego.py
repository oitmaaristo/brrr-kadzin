import logging
import re

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper, CarListing

logger = logging.getLogger(__name__)

# Veego make IDs (from api.veego.ee/api/attr/vehicles/makes)
VEEGO_MAKE_IDS = {
    "bmw": 19, "audi": 2, "mercedes-benz": 41, "ford": 8, "opel": 30,
    "skoda": 35, "volvo": 39, "toyota": 37, "volkswagen": 40, "renault": 33,
    "peugeot": 32, "hyundai": 12, "kia": 16, "honda": 11, "mitsubishi": 26,
    "nissan": 28, "mazda": 22, "dacia": 6, "tesla": 36, "citroen": 5,
    "fiat": 7, "saab": 34, "seat": 43, "subaru": 42, "suzuki": 44,
    "jaguar": 14, "land rover": 18, "lexus": 20, "mini": 24, "porsche": 31,
}


class VeegoScraper(BaseScraper):
    """Scraper for veego.ee.

    Verified from live site (2026-03):
    - Results URL: https://veego.ee/en/used-vehicles?make_id=19&is_new=0&per_page=30&page=1
    - API endpoint: api.veego.ee/api/v2/search (called by the page JS)
    - Listing card: div.results-card or a[href*="/used-vehicles/"]
    - Title: h3.card-title
    - Price: p.active-price
    - Year+mileage+fuel+gear: p.year-odo-fuel-gear
    - Location: span.address-text
    - Seller: p.company-name
    - Image: img inside swiper-container
    - Link: a[href*="/used-vehicles/{id}-"]
    """

    PORTAL_NAME = "veego"
    BASE_URL = "https://veego.ee"

    def build_search_url(self, params: dict) -> str:
        """Build veego.ee search URL with verified query params."""
        query_parts = ["is_new=0", "per_page=30", "page=1"]

        brand = params.get("brand", "").lower().strip()
        if brand:
            make_id = VEEGO_MAKE_IDS.get(brand)
            if make_id:
                query_parts.append(f"make_id={make_id}")

        if params.get("year_min"):
            query_parts.append(f"year_from={params['year_min']}")
        if params.get("year_max"):
            query_parts.append(f"year_to={params['year_max']}")
        if params.get("price_min"):
            query_parts.append(f"price_from={params['price_min']}")
        if params.get("price_max"):
            query_parts.append(f"price_to={params['price_max']}")

        url = f"{self.BASE_URL}/en/used-vehicles?{'&'.join(query_parts)}"
        return url

    async def scrape(self, params: dict) -> list[CarListing]:
        """Scrape veego.ee listings."""
        url = self.build_search_url(params)
        logger.info(f"[veego] Scraping: {url}")

        page = await self._new_page()
        listings = []

        try:
            await self._random_delay(1.0, 3.0)
            response = await page.goto(url, wait_until="networkidle", timeout=30000)

            if not response:
                logger.warning("[veego] No response received")
                return listings

            status = response.status
            if status != 200:
                logger.warning(f"[veego] Got status {status}")
                return listings

            # Wait for listings to render (JS/Nuxt app)
            try:
                await page.wait_for_selector('a[href*="/used-vehicles/"]', timeout=10000)
            except Exception:
                logger.info("[veego] No vehicle links appeared within timeout")

            await self._random_delay(1.0, 2.0)

            html = await page.content()
            listings = self._parse_listings(html, params)

            if not listings:
                title = await page.title()
                logger.info(f"[veego] Page title: {title}, HTML length: {len(html)}")

            logger.info(f"[veego] Found {len(listings)} listings")

        except Exception as e:
            logger.error(f"[veego] Scraping error: {e}")
        finally:
            await page.close()

        return listings

    def _parse_listings(self, html: str, params: dict | None = None) -> list[CarListing]:
        """Parse listings from veego.ee HTML."""
        params = params or {}
        soup = BeautifulSoup(html, "lxml")
        listings = []

        mileage_max = params.get("mileage_max")
        exclude_keywords = [kw.strip().lower() for kw in params.get("exclude_keywords", "").split(",") if kw.strip()] if params.get("exclude_keywords") else []

        # Find all vehicle links
        vehicle_links = soup.select('a[href*="/used-vehicles/"][href*="-"]')
        if not vehicle_links:
            return listings

        seen_ids = set()
        for link_el in vehicle_links:
            try:
                href = link_el.get("href", "")
                if not href:
                    continue

                # Extract ID: /en/used-vehicles/145735-bmw-m5-...
                id_match = re.search(r"/used-vehicles/(\d+)-", href)
                if not id_match:
                    continue
                external_id = id_match.group(1)

                if external_id in seen_ids:
                    continue
                seen_ids.add(external_id)

                url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

                # Navigate to the card container
                card = link_el
                for _ in range(3):
                    parent = card.parent
                    if parent and "results-card" in " ".join(parent.get("class", [])):
                        card = parent
                        break
                    if parent and "result-col" in " ".join(parent.get("class", [])):
                        card = parent
                        break
                    card = parent if parent else card

                # Title
                title = "Unknown"
                title_el = card.select_one("h3.card-title")
                if not title_el:
                    title_el = card.select_one("h3, h2")
                if title_el:
                    title = title_el.get_text(strip=True)

                # Price
                price = None
                price_el = card.select_one("p.active-price, .active-price")
                if price_el:
                    price_text = price_el.get_text(strip=True)
                    digits = re.sub(r"[^\d]", "", price_text)
                    price = int(digits) if digits else None

                # Year, mileage, fuel, gear from "2020•67 000 km•P•A"
                year = None
                mileage = None
                fuel_type = None
                transmission = None
                info_el = card.select_one("p.year-odo-fuel-gear")
                if info_el:
                    info_text = info_el.get_text(" ", strip=True)
                    # Year
                    year_match = re.search(r"\b(19|20)\d{2}\b", info_text)
                    if year_match:
                        year = int(year_match.group(0))
                    # Mileage
                    km_match = re.search(r"([\d\s]+)\s*km", info_text)
                    if km_match:
                        km_digits = re.sub(r"[^\d]", "", km_match.group(1))
                        mileage = int(km_digits) if km_digits else None

                    # Fuel from span.fuel-value
                    fuel_el = card.select_one("span.fuel-value")
                    if fuel_el:
                        fuel_abbr = fuel_el.get_text(strip=True)
                        fuel_map = {"P": "Petrol", "D": "Diesel", "E": "Electric",
                                    "HP": "Hybrid Petrol", "HD": "Hybrid Diesel",
                                    "CNG": "CNG", "LPG": "LPG"}
                        fuel_type = fuel_map.get(fuel_abbr, fuel_abbr)

                    # Transmission from span.gear-value
                    gear_el = card.select_one("span.gear-value")
                    if gear_el:
                        gear_abbr = gear_el.get_text(strip=True)
                        gear_map = {"A": "Automatic", "M": "Manual"}
                        transmission = gear_map.get(gear_abbr, gear_abbr)

                # Client-side mileage filtering
                if mileage_max and mileage and mileage > mileage_max:
                    continue

                # Exclude keywords filter
                if exclude_keywords and title:
                    title_lower = title.lower()
                    if any(kw in title_lower for kw in exclude_keywords):
                        continue

                # Location
                location = None
                loc_el = card.select_one("span.address-text, p.address-rating")
                if loc_el:
                    location = loc_el.get_text(strip=True) or None

                # Image - look for img.image (vehicle photos) first,
                # then any img with api.veego.ee URL, skip SVG placeholders
                image_url = None
                img_el = card.select_one("img.image")
                if not img_el:
                    # Fallback: find any img whose src points to the API
                    for candidate in card.select("img"):
                        candidate_src = candidate.get("src", "")
                        if "api.veego.ee" in candidate_src:
                            img_el = candidate
                            break
                if img_el:
                    src = img_el.get("src") or img_el.get("data-src") or ""
                    if src and not src.startswith("data:"):
                        image_url = src

                listings.append(
                    CarListing(
                        portal="veego",
                        external_id=external_id,
                        url=url,
                        title=title,
                        price=price,
                        year=year,
                        mileage=mileage,
                        fuel_type=fuel_type,
                        transmission=transmission,
                        location=location,
                        image_url=image_url,
                    )
                )
            except Exception as e:
                logger.debug(f"[veego] Failed to parse listing: {e}")
                continue

        return listings
