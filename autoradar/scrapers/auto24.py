import logging
import re
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper, CarListing

logger = logging.getLogger(__name__)

# auto24.ee brand codes (b parameter) - most common brands
# Full list needs to be scraped from the search form dropdown
BRAND_CODES = {
    "audi": 6,
    "bmw": 2,
    "citroen": 27,
    "dacia": 72,
    "fiat": 26,
    "ford": 7,
    "honda": 8,
    "hyundai": 41,
    "jaguar": 35,
    "kia": 33,
    "land rover": 36,
    "lexus": 37,
    "mazda": 16,
    "mercedes-benz": 1,
    "mini": 48,
    "mitsubishi": 17,
    "nissan": 18,
    "opel": 5,
    "peugeot": 3,
    "porsche": 31,
    "renault": 4,
    "saab": 19,
    "seat": 34,
    "skoda": 40,
    "subaru": 20,
    "suzuki": 22,
    "tesla": 83,
    "toyota": 9,
    "volkswagen": 11,
    "volvo": 10,
}

# Fuel type codes (ak parameter)
FUEL_CODES = {
    "petrol": 1,
    "bensiin": 1,
    "diesel": 2,
    "diisel": 2,
    "lpg": 4,
    "gaas": 4,
    "electric": 6,
    "elektri": 6,
    "hybrid": 5,
    "hübriid": 5,
    "plug-in hybrid": 7,
    "plug-in hübriid": 7,
}

# Transmission codes (f parameter)
TRANSMISSION_CODES = {
    "manual": 1,
    "manuaal": 1,
    "automatic": 2,
    "automaat": 2,
}

# Body type codes (e parameter)
BODY_TYPE_CODES = {
    "sedan": 1,
    "sedaan": 1,
    "wagon": 2,
    "universaal": 2,
    "hatchback": 3,
    "luukpära": 3,
    "suv": 5,
    "maastur": 5,
    "coupe": 6,
    "kupee": 6,
    "cabriolet": 7,
    "kabrio": 7,
    "van": 8,
    "kaubik": 8,
    "minivan": 9,
    "mpv": 9,
}

# Drive type codes (g parameter)
DRIVE_TYPE_CODES = {
    "fwd": 1,
    "esisild": 1,
    "rwd": 2,
    "tagasild": 2,
    "awd": 3,
    "nelik": 3,
    "4wd": 3,
}


class Auto24Scraper(BaseScraper):
    """Scraper for auto24.ee - Estonia's largest car portal."""

    PORTAL_NAME = "auto24"
    BASE_URL = "https://www.auto24.ee/kasutatud/nimekiri.php"

    def build_search_url(self, params: dict) -> str:
        """Build auto24.ee search URL from filter parameters.

        Supported params:
            brand, model_code, price_min, price_max, year_min, year_max,
            mileage_max, fuel_type, transmission, body_type, drive_type,
            engine_min, engine_max, power_min, power_max, color, location,
            seller_type, sort_by
        """
        query = {}

        # Category: default to passenger cars + SUVs
        query["a"] = params.get("category", "100")

        # Brand
        brand = params.get("brand", "").lower()
        if brand and brand in BRAND_CODES:
            query["b"] = BRAND_CODES[brand]

        # Model (needs brand-specific model code)
        model_code = params.get("model_code")
        if model_code:
            query["bw"] = model_code

        # Price range
        if params.get("price_min"):
            query["ag"] = params["price_min"]
        if params.get("price_max"):
            query["ah"] = params["price_max"]

        # Year range
        if params.get("year_min"):
            query["ae"] = params["year_min"]
        if params.get("year_max"):
            query["af"] = params["year_max"]

        # Mileage
        if params.get("mileage_max"):
            query["aj"] = params["mileage_max"]

        # Fuel type
        fuel = params.get("fuel_type", "").lower()
        if fuel and fuel in FUEL_CODES:
            query["ak"] = FUEL_CODES[fuel]

        # Transmission
        trans = params.get("transmission", "").lower()
        if trans and trans in TRANSMISSION_CODES:
            query["f"] = TRANSMISSION_CODES[trans]

        # Body type
        body = params.get("body_type", "").lower()
        if body and body in BODY_TYPE_CODES:
            query["e"] = BODY_TYPE_CODES[body]

        # Drive type
        drive = params.get("drive_type", "").lower()
        if drive and drive in DRIVE_TYPE_CODES:
            query["g"] = DRIVE_TYPE_CODES[drive]

        # Engine volume (cm³)
        if params.get("engine_min"):
            query["ai"] = params["engine_min"]
        if params.get("engine_max"):
            query["al"] = params["engine_max"]

        # Power (kW)
        if params.get("power_min"):
            query["am"] = params["power_min"]
        if params.get("power_max"):
            query["an"] = params["power_max"]

        # Sort by newest first
        query["by"] = params.get("sort_by", "3")

        return f"{self.BASE_URL}?{urlencode(query)}"

    async def scrape(self, params: dict) -> list[CarListing]:
        """Scrape auto24.ee listings matching the given parameters."""
        url = self.build_search_url(params)
        logger.info(f"[auto24] Scraping: {url}")

        page = await self._new_page()
        listings = []

        try:
            # Navigate to search results
            await self._random_delay(1.0, 2.5)
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            if not response or response.status != 200:
                logger.warning(f"[auto24] Got status {response.status if response else 'None'}")
                return listings

            # Wait for results to load
            await page.wait_for_selector(
                "#usedVehiclesSearchResult-flex, .result-row, .no-results",
                timeout=15000,
            )

            # Small delay to let dynamic content load
            await self._random_delay(0.5, 1.5)

            # Get page HTML
            html = await page.content()
            listings = self._parse_listings(html)

            logger.info(f"[auto24] Found {len(listings)} listings")

        except Exception as e:
            logger.error(f"[auto24] Scraping error: {e}")
        finally:
            await page.close()

        return listings

    def _parse_listings(self, html: str) -> list[CarListing]:
        """Parse car listings from auto24.ee HTML."""
        soup = BeautifulSoup(html, "lxml")
        listings = []

        rows = soup.select(".result-row")
        if not rows:
            # Try alternative selector
            rows = soup.select('[class*="result-row"]')

        for row in rows:
            try:
                listing = self._parse_single_listing(row)
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.debug(f"[auto24] Failed to parse row: {e}")
                continue

        return listings

    def _parse_single_listing(self, row) -> CarListing | None:
        """Parse a single listing row from auto24.ee."""
        # Extract link and ID
        link_el = row.select_one("a[href]")
        if not link_el:
            return None

        href = link_el.get("href", "")
        if not href:
            return None

        # Build full URL
        if href.startswith("/"):
            url = f"https://www.auto24.ee{href}"
        elif not href.startswith("http"):
            url = f"https://www.auto24.ee/{href}"
        else:
            url = href

        # Extract external ID from URL
        # URLs look like: /kasutatud/12345678 or /used/12345678
        external_id = self._extract_id(url)
        if not external_id:
            return None

        # Model / title
        model_el = row.select_one(".model")
        title_parts = []

        # Try to get brand from broader context
        brand_el = row.select_one(".make") or row.select_one("span.make")
        if brand_el:
            title_parts.append(brand_el.get_text(strip=True))

        if model_el:
            title_parts.append(model_el.get_text(strip=True))

        # Engine info
        engine_el = row.select_one(".engine")
        engine_text = engine_el.get_text(strip=True) if engine_el else None
        if engine_text:
            title_parts.append(engine_text)

        title = " ".join(title_parts) if title_parts else "Unknown"

        # Price
        price = self._parse_price(row)

        # Year
        year = self._parse_field_int(row, ".year", "year")

        # Mileage
        mileage = self._parse_mileage(row)

        # Transmission
        trans_el = row.select_one(".transmission") or row.select_one('[class*="transmission"]')
        transmission = trans_el.get_text(strip=True) if trans_el else None

        # Fuel type from engine text (e.g., "2.0 TDI" -> diesel)
        fuel_type = self._guess_fuel_from_engine(engine_text) if engine_text else None

        # Location
        location_el = row.select_one(".location") or row.select_one('[class*="location"]')
        location = location_el.get_text(strip=True) if location_el else None

        # Image
        img_el = row.select_one("img")
        image_url = None
        if img_el:
            image_url = img_el.get("src") or img_el.get("data-src")

        return CarListing(
            portal="auto24",
            external_id=external_id,
            url=url,
            title=title,
            price=price,
            year=year,
            mileage=mileage,
            fuel_type=fuel_type,
            transmission=transmission,
            image_url=image_url,
            location=location,
            raw_data={"engine": engine_text},
        )

    def _extract_id(self, url: str) -> str | None:
        """Extract listing ID from auto24.ee URL."""
        # Pattern: /kasutatud/1234567 or /used/1234567
        match = re.search(r"/(?:kasutatud|used)/(\d+)", url)
        if match:
            return match.group(1)
        # Fallback: any long number sequence in URL
        match = re.search(r"/(\d{5,})", url)
        if match:
            return match.group(1)
        return None

    def _parse_price(self, row) -> int | None:
        """Extract price as integer from a listing row.

        auto24.ee price text starts with a currency symbol (first char stripped).
        Price is in a span.price element, often nested inside another span.
        """
        # Primary: span.price (confirmed selector)
        el = row.select_one("span.price")
        if el:
            text = el.get_text(strip=True)
            # Strip leading currency symbol
            if text and not text[0].isdigit():
                text = text[1:]
            return self._text_to_int(text)

        # Fallback selectors
        for selector in [".price", '[class*="price"]']:
            el = row.select_one(selector)
            if el:
                text = el.get_text(strip=True)
                return self._text_to_int(text)

        # Last resort: look for currency sign
        for span in row.select("span"):
            text = span.get_text(strip=True)
            if "€" in text or "EUR" in text:
                return self._text_to_int(text)

        return None

    def _parse_mileage(self, row) -> int | None:
        """Extract mileage as integer."""
        el = row.select_one(".mileage") or row.select_one('[class*="mileage"]')
        if el:
            text = el.get_text(strip=True)
            return self._text_to_int(text)
        return None

    def _parse_field_int(self, row, selector: str, class_name: str) -> int | None:
        """Extract an integer field by CSS selector or class attribute."""
        el = row.select_one(selector) or row.select_one(f'[class*="{class_name}"]')
        if el:
            text = el.get_text(strip=True)
            return self._text_to_int(text)
        return None

    @staticmethod
    def _text_to_int(text: str) -> int | None:
        """Convert text like '14 500 €' or '87 000 km' to int.

        Handles non-breaking spaces (\xa0) which auto24.ee uses in mileage.
        """
        # Replace non-breaking spaces and remove everything except digits
        cleaned = text.replace("\xa0", "")
        digits = re.sub(r"[^\d]", "", cleaned)
        if digits:
            return int(digits)
        return None

    @staticmethod
    def _guess_fuel_from_engine(engine_text: str) -> str | None:
        """Try to guess fuel type from engine description."""
        text = engine_text.lower()
        if any(kw in text for kw in ["tdi", "cdi", "hdi", "d4d", "dci", "diesel", "diisel"]):
            return "diesel"
        if any(kw in text for kw in ["tsi", "tfsi", "turbo", "gti", "bensiin", "petrol"]):
            return "petrol"
        if "electric" in text or "elektri" in text or "ev" in text:
            return "electric"
        if "hybrid" in text or "hübriid" in text:
            return "hybrid"
        return None
